"""
导入服务模块
处理 Word 文档导入和数据存储
"""

import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from ..parsers.word_parser import parse_word_document
from .project_section_matcher import ProjectSectionMatcher
from .issue_category_classifier import IssueCategoryClassifier

# 配置日志
logger = logging.getLogger(__name__)


class ImportService:
    """导入服务"""

    def __init__(self, db_path: str):
        """
        初始化导入服务

        Args:
            db_path: 数据库路径
        """
        self.db_path = db_path

    def import_word_document(self, file_path: str) -> Dict:
        """
        导入 Word 文档

        Args:
            file_path: Word 文件路径

        Returns:
            导入结果
        """
        # 解析文档
        parse_result = parse_word_document(file_path)

        if parse_result.get('status') == 'error':
            return {
                'success': False,
                'file_name': parse_result['file_name'],
                'error': parse_result['error']
            }

        try:
            # 存储到数据库
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 0. 检查通知书是否已存在（重复检测）
            cursor.execute(
                "SELECT id FROM supervision_notices WHERE notice_number = ?",
                (parse_result['notice_number'],)
            )
            existing_notice = cursor.fetchone()

            if existing_notice:
                conn.close()
                return {
                    'success': False,
                    'duplicate': True,
                    'notice_number': parse_result['notice_number'],
                    'file_name': parse_result['file_name'],
                    'error': f"通知书编号 {parse_result['notice_number']} 已存在，无需重复导入"
                }

            # 1. 插入监督通知书
            notice_id = self._insert_supervision_notice(
                cursor,
                parse_result
            )

            # 2. 插入项目和标段（从通知书级别的数据）
            project_result = self._insert_project(
                cursor,
                parse_result
            )

            if not project_result:
                conn.close()
                return {
                    'success': False,
                    'file_name': parse_result['file_name'],
                    'error': '项目插入失败'
                }

            project_id = project_result['id']
            project_match_info = {
                'status': project_result['status'],
                'message': project_result['message']
            }

            # 3. 插入下发整改通知单的问题
            rectification_count = 0
            issues_list = []
            for issue in parse_result['rectification_notices']:
                issue_id = self._insert_issue(cursor, notice_id, issue, project_id)
                if issue_id:
                    rectification_count += 1
                    issues_list.append({
                        'id': issue_id,
                        'site_name': issue.get('site_name'),
                        'section_name': issue.get('section_name'),
                        'description': issue.get('description'),
                        'is_rectification_notice': True,
                        'document_section': 'rectification'
                    })

            # 4. 插入其它问题
            other_count = 0
            for issue in parse_result['other_issues']:
                issue_id = self._insert_issue(cursor, notice_id, issue, project_id)
                if issue_id:
                    other_count += 1
                    issues_list.append({
                        'id': issue_id,
                        'site_name': issue.get('site_name'),
                        'section_name': issue.get('section_name'),
                        'description': issue.get('description'),
                        'is_rectification_notice': False,
                        'document_section': 'other'
                    })

            conn.commit()
            conn.close()

            return {
                'success': True,
                'file_name': parse_result['file_name'],
                'notice_number': parse_result['notice_number'],
                'check_date': parse_result.get('check_date'),
                'check_unit': parse_result.get('inspection_unit') or parse_result.get('check_unit'),
                'check_personnel': parse_result.get('inspection_personnel') or parse_result.get('check_personnel'),
                'builder_unit': parse_result.get('builder_unit'),
                'project_name': parse_result.get('project_name'),
                'rectification_notices': rectification_count,
                'other_issues': other_count,
                'total_issues': rectification_count + other_count,
                'quality_issues_count': 0,
                'safety_issues_count': 0,
                'management_issues_count': 0,
                'total_issues_count': rectification_count + other_count,
                'issues': issues_list,
                'project_match_info': project_match_info  # 添加项目匹配信息
            }

        except Exception as e:
            return {
                'success': False,
                'file_name': parse_result['file_name'],
                'error': str(e)
            }

    def _insert_project(self, cursor, parse_result: Dict) -> Optional[Dict]:
        """
        插入项目（从通知书级别的数据）

        使用匹配器进行项目名匹配，支持完全匹配、相近匹配和新增

        Returns:
            项目信息字典，包含：
            - id: 项目 ID
            - name: 项目名
            - status: 'exact' | 'similar' | 'new'
            - message: 提示信息
        """
        try:
            project_name = parse_result.get('project_name') or '未知项目'
            builder_unit = parse_result.get('builder_unit')

            # 使用匹配器进行项目匹配
            matcher = ProjectSectionMatcher(self.db_path)
            match_result = matcher.match_project(project_name)

            if match_result['status'] == 'error':
                logger.error(f"❌ 项目匹配失败: {match_result['message']}")
                return None

            # 如果是完全匹配或相近匹配，直接返回
            if match_result['status'] in ['exact', 'similar']:
                return {
                    'id': match_result['project_id'],
                    'name': match_result['project_name'],
                    'status': match_result['status'],
                    'message': match_result['message']
                }

            # 如果是新项目，插入数据库
            if match_result['status'] == 'new':
                cursor.execute("""
                    INSERT INTO projects
                    (project_name, builder_unit)
                    VALUES (?, ?)
                """, (
                    project_name,
                    builder_unit
                ))

                project_id = cursor.lastrowid
                return {
                    'id': project_id,
                    'name': project_name,
                    'status': 'new',
                    'message': match_result['message']
                }

        except Exception as e:
            logger.error(f"❌ 插入项目失败: {e}")
            return None

    def _insert_supervision_notice(self, cursor, parse_result: Dict) -> Optional[int]:
        """
        插入监督通知书

        Returns:
            通知书 ID
        """
        try:
            # 插入新记录
            cursor.execute("""
                INSERT INTO supervision_notices
                (notice_number, check_date, check_unit, check_personnel, inspection_basis)
                VALUES (?, ?, ?, ?, ?)
            """, (
                parse_result['notice_number'],
                parse_result['check_date'],
                parse_result['check_unit'],
                parse_result['check_personnel'],
                parse_result.get('inspection_basis')
            ))

            return cursor.lastrowid

        except Exception as e:
            logger.error(f"❌ 插入监督通知书失败: {e}")
            return None

    def _insert_issue(self, cursor, notice_id: int, issue: Dict, project_id: int) -> Optional[int]:
        """
        插入隐患问题

        Args:
            cursor: 数据库游标
            notice_id: 通知书 ID
            issue: 问题数据
            project_id: 项目 ID

        Returns:
            问题 ID
        """
        try:
            # 解析标段信息：优先使用 sections 中的权威数据；没有则用识别结果；都没有则留空
            recognized_section_id = issue.get('section_id')
            recognized_section_name = issue.get('section_name')
            logger.info(f"\n[DEBUG] 处理标段信息:")
            logger.info(f"   recognized_section_id: {recognized_section_id}")
            logger.info(f"   recognized_section_name: {recognized_section_name}")
            logger.info(f"   project_id: {project_id}")

            final_section_id = None
            final_section_name = None
            final_contractor = issue.get('contractor')
            final_supervisor = issue.get('supervisor')

            # 情况1：识别出了 section_id，尝试从 sections 读取
            if recognized_section_id:
                cursor.execute(
                    "SELECT id, section_name, contractor_unit, supervisor_unit FROM sections WHERE id = ?",
                    (recognized_section_id,)
                )
                row = cursor.fetchone()
                if row:
                    final_section_id = row[0]
                    final_section_name = row[1]
                    final_contractor = row[2] or final_contractor
                    final_supervisor = row[3] or final_supervisor
                    logger.info(f"[DEBUG] 使用 sections 表数据: id={final_section_id}, name={final_section_name}")
                else:
                    # 找不到该 id，则退回使用识别的名称
                    final_section_name = recognized_section_name
                    logger.info("[DEBUG] 未在 sections 通过 id 找到，使用识别的 section_name")

            # 情况2：没有 section_id，但有 section_name，尝试匹配现有 sections（不创建）
            elif recognized_section_name:
                cursor.execute(
                    "SELECT id, section_name, contractor_unit, supervisor_unit FROM sections WHERE project_id = ? AND section_name = ?",
                    (project_id, recognized_section_name)
                )
                row = cursor.fetchone()
                if row:
                    final_section_id = row[0]
                    final_section_name = row[1]
                    final_contractor = row[2] or final_contractor
                    final_supervisor = row[3] or final_supervisor
                    logger.info(f"[DEBUG] 通过名称匹配到 sections: id={final_section_id}, name={final_section_name}")
                else:
                    final_section_name = recognized_section_name
                    logger.info("[DEBUG] 名称在 sections 未匹配，保留识别的 section_name，不创建新标段")

            # 情况3：两者都没有，保持空白
            else:
                logger.info("[DEBUG] 未提供 section_id 或 section_name，相关字段保持空白")

            # 生成问题编号（临时）
            issue_number = f"ISSUE_{notice_id}_{datetime.now().timestamp()}"

            # 使用本地时间戳而不是 SQLite 的 UTC 时间戳
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 优先使用用户编辑的问题类别，只在为空时才使用自动分类
            issue_category = issue.get('issue_category')

            if not issue_category:
                # 使用分类器自动识别问题类别
                issue_category = IssueCategoryClassifier.classify(
                    description=issue['description'],
                    site_name=issue.get('site_name'),
                    section_name=final_section_name
                )

                # 如果分类器无法识别，默认设为施工安全
                if not issue_category or issue_category == '其它':
                    issue_category = '施工安全'

            logger.info(f"[DEBUG] 问题类别来源: {'用户编辑' if issue.get('issue_category') else '自动分类'}")
            logger.info(f"[DEBUG] issue_category: {issue_category}")
            logger.info(f"[DEBUG] issue_type_level1: {issue.get('issue_type_level1')}")
            logger.info(f"[DEBUG] issue_type_level2: {issue.get('issue_type_level2')}")

            logger.info(f"\n[DEBUG] 准备插入问题记录:")
            logger.info(f"   issue_number: {issue_number}")
            logger.info(f"   supervision_notice_id: {notice_id}")
            logger.info(f"   final_section_id: {final_section_id}")
            logger.info(f"   final_section_name: {final_section_name}")
            logger.info(f"   site_name: {issue.get('site_name')}")
            logger.info(f"   final_contractor: {final_contractor}")
            logger.info(f"   final_supervisor: {final_supervisor}")
            logger.info(f"   description: {issue['description'][:100]}...")
            logger.info(f"   is_rectification_notice: {issue['is_rectification_notice']}")
            logger.info(f"   is_bad_behavior_notice: {issue.get('is_bad_behavior_notice', False)}")
            logger.info(f"   document_section: {issue['document_section']}")
            logger.info(f"   issue_category: {issue_category}")
            logger.info(f"   inspection_unit: {issue.get('inspection_unit')}")
            logger.info(f"   inspection_date: {issue.get('inspection_date')}")
            logger.info(f"   inspection_personnel: {issue.get('inspection_personnel')}")
            logger.info(f"   rectification_requirements: {issue.get('rectification_requirements')}")
            logger.info(f"   rectification_deadline: {issue.get('rectification_deadline')}")
            logger.info(f"   responsible_unit: {issue.get('responsible_unit')}")

            try:
                cursor.execute("""
                    INSERT INTO issues
                    (issue_number, supervision_notice_id, section_id, section_name, site_name, contractor, supervisor, description,
                     is_rectification_notice, is_bad_behavior_notice, document_section, document_source,
                     severity, issue_category, issue_type_level1, issue_type_level2, inspection_unit, inspection_date, inspection_personnel,
                     rectification_requirements, rectification_deadline, responsible_unit, responsible_person,
                     created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    issue_number,
                    notice_id,
                    final_section_id,
                    final_section_name,
                    issue.get('site_name'),
                    final_contractor,
                    final_supervisor,
                    issue['description'],
                    issue['is_rectification_notice'],
                    issue.get('is_bad_behavior_notice', False),
                    issue['document_section'],
                    'word',
                    3,  # 默认等级为 3
                    issue_category,  # 使用用户编辑的分类或自动分类
                    issue.get('issue_type_level1'),  # 用户编辑的二级分类
                    issue.get('issue_type_level2'),  # 用户编辑的三级分类
                    issue.get('inspection_unit'),
                    issue.get('inspection_date'),
                    issue.get('inspection_personnel'),
                    issue.get('rectification_requirements'),
                    issue.get('rectification_deadline'),
                    issue.get('responsible_unit'),
                    issue.get('responsible_person'),
                    now,
                    now
                ))
                issue_id = cursor.lastrowid
                logger.info(f"[DEBUG] ✅ 问题插入成功: issue_id={issue_id}")
                return issue_id
            except Exception as issue_err:
                logger.error(f"[ERROR] ❌ 问题插入失败: {issue_err}")
                logger.error(f"   错误类型: {type(issue_err).__name__}")
                raise

        except Exception as e:
            logger.error(f"❌ 插入隐患问题失败: {e}")
            logger.error(f"   问题数据: {issue}")
            logger.error(f"   通知书 ID: {notice_id}, 项目 ID: {project_id}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def recognize_word_document(self, file_path: str) -> Dict:
        """
        识别 Word 文档（只识别不导入）

        Args:
            file_path: Word 文件路径

        Returns:
            识别结果（包含通知书和问题列表，但不导入数据库）
        """
        # 解析文档
        parse_result = parse_word_document(file_path)

        if parse_result.get('status') == 'error':
            return {
                'success': False,
                'file_name': parse_result['file_name'],
                'error': parse_result['error']
            }

        try:
            # 检查通知书是否已存在（重复检测）
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id FROM supervision_notices WHERE notice_number = ?",
                (parse_result['notice_number'],)
            )
            existing_notice = cursor.fetchone()
            conn.close()

            if existing_notice:
                return {
                    'success': False,
                    'duplicate': True,
                    'notice_number': parse_result['notice_number'],
                    'file_name': parse_result['file_name'],
                    'error': f"通知书编号 {parse_result['notice_number']} 已存在，无需重复导入"
                }

            # 处理问题列表
            issues_list = []

            # 处理下发整改通知单的问题
            for issue in parse_result['rectification_notices']:
                issues_list.append({
                    'id': f"temp_{len(issues_list)}",
                    'site_name': issue.get('site_name'),
                    'section_name': issue.get('section_name'),
                    'section_code': issue.get('section_code'),
                    'description': issue.get('description'),
                    'is_rectification_notice': True,
                    'document_section': 'rectification',
                    'contractor': issue.get('contractor'),
                    'supervisor': issue.get('supervisor'),
                    'inspection_unit': issue.get('inspection_unit'),
                    'inspection_date': issue.get('inspection_date'),
                    'inspection_personnel': issue.get('inspection_personnel'),
                    'rectification_requirements': issue.get('rectification_requirements'),
                    'rectification_deadline': issue.get('rectification_deadline'),
                    'responsible_unit': issue.get('responsible_unit')
                })

            # 处理其它问题
            for issue in parse_result['other_issues']:
                issues_list.append({
                    'id': f"temp_{len(issues_list)}",
                    'site_name': issue.get('site_name'),
                    'section_name': issue.get('section_name'),
                    'section_code': issue.get('section_code'),
                    'description': issue.get('description'),
                    'is_rectification_notice': False,
                    'document_section': 'other',
                    'contractor': issue.get('contractor'),
                    'supervisor': issue.get('supervisor'),
                    'inspection_unit': issue.get('inspection_unit'),
                    'inspection_date': issue.get('inspection_date'),
                    'inspection_personnel': issue.get('inspection_personnel'),
                    'rectification_requirements': issue.get('rectification_requirements'),
                    'rectification_deadline': issue.get('rectification_deadline'),
                    'responsible_unit': issue.get('responsible_unit')
                })

            return {
                'success': True,
                'file_name': parse_result['file_name'],
                'notice_number': parse_result['notice_number'],
                'check_date': parse_result.get('check_date'),
                'check_unit': parse_result.get('inspection_unit') or parse_result.get('check_unit'),
                'check_personnel': parse_result.get('inspection_personnel') or parse_result.get('check_personnel'),
                'builder_unit': parse_result.get('builder_unit'),
                'project_name': parse_result.get('project_name'),
                'rectification_notices_count': len(parse_result['rectification_notices']),
                'other_issues_count': len(parse_result['other_issues']),
                'total_issues_count': len(issues_list),
                'issues': issues_list
            }

        except Exception as e:
            return {
                'success': False,
                'file_name': parse_result['file_name'],
                'error': str(e)
            }

    def import_batch_documents(self, folder_path: str) -> Dict:
        """
        批量导入 Word 文档

        Args:
            folder_path: 文件夹路径

        Returns:
            批量导入结果
        """
        folder = Path(folder_path)
        results = {
            'total_files': 0,
            'successful': 0,
            'failed': 0,
            'total_issues': 0,
            'details': []
        }

        # 查找所有 Word 文件（排除临时文件）
        word_files = [
            f for f in list(folder.glob('*.docx')) + list(folder.glob('*.doc'))
            if not f.name.startswith('~$')  # 排除临时文件
        ]
        results['total_files'] = len(word_files)

        for file_path in word_files:
            result = self.import_word_document(str(file_path))

            if result['success']:
                results['successful'] += 1
                results['total_issues'] += result['total_issues']
            else:
                results['failed'] += 1

            results['details'].append(result)

        return results

    def import_selected_issues(self, notice_data: Dict, selected_issue_ids: List[str]) -> Dict:
        """
        导入选中的问题

        Args:
            notice_data: 通知书数据（来自识别结果）
            selected_issue_ids: 选中的问题 ID 列表

        Returns:
            导入结果
        """
        try:
            logger.info(f"\n📋 开始导入选中的问题")
            logger.info(f"   选中的问题 ID 列表: {selected_issue_ids}")
            logger.info(f"   选中的问题数量: {len(selected_issue_ids)}")
            logger.info(f"   通知书中的总问题数: {len(notice_data.get('issues', []))}")

            # 确保 selected_issue_ids 是整数列表，以防前端数据类型错误
            logger.info(f"🔍 [DEBUG] 原始 selected_issue_ids: {selected_issue_ids}")
            logger.info(f"🔍 [DEBUG] selected_issue_ids 类型: {type(selected_issue_ids)}")
            logger.info(f"🔍 [DEBUG] 第一个元素类型: {type(selected_issue_ids[0]) if selected_issue_ids else 'N/A'}")

            selected_issue_ids = [int(i) for i in selected_issue_ids]
            logger.info(f"🔍 [DEBUG] 转换后 selected_issue_ids: {selected_issue_ids}")


            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 1. 检查通知书是否已存在
            cursor.execute(
                "SELECT id FROM supervision_notices WHERE notice_number = ?",
                (notice_data['notice_number'],)
            )
            existing_notice = cursor.fetchone()

            if existing_notice:
                conn.close()
                return {
                    'success': False,
                    'duplicate': True,
                    'notice_number': notice_data['notice_number'],
                    'error': f"通知书编号 {notice_data['notice_number']} 已存在"
                }

            # 2. 插入监督通知书
            notice_id = self._insert_supervision_notice_from_data(cursor, notice_data)
            logger.info(f"🔍 [DEBUG] 通知书插入结果 notice_id: {notice_id}")
            if not notice_id:
                conn.close()
                return {
                    'success': False,
                    'error': '通知书插入失败'
                }

            # 3. 插入项目
            project_result = self._insert_project_from_data(cursor, notice_data)
            logger.info(f"🔍 [DEBUG] 项目插入结果: {project_result}")
            if not project_result:
                conn.close()
                return {
                    'success': False,
                    'error': '项目插入失败'
                }

            project_id = project_result['id']
            logger.info(f"🔍 [DEBUG] project_id: {project_id}")

            # 4. 导入选中的问题
            imported_issues = []
            skipped_issues = []
            failed_issues = []

            logger.info(f"\n🔍 [DEBUG] 开始遍历问题列表:")
            issues_list = notice_data.get('issues', [])
            logger.info(f"🔍 [DEBUG] 问题列表长度: {len(issues_list)}")

            for idx, issue_data in enumerate(issues_list):
                logger.info(f"\n🔍 [DEBUG] 检查问题 idx={idx}")
                logger.info(f"🔍 [DEBUG] idx 类型: {type(idx)}")
                logger.info(f"🔍 [DEBUG] idx in selected_issue_ids: {idx in selected_issue_ids}")
                logger.info(f"🔍 [DEBUG] 问题描述: {issue_data.get('description', '')[:50]}...")

                # 使用数组索引进行匹配（前端传递的是索引）
                if idx in selected_issue_ids:
                    logger.info(f"   ✓ 导入问题 {idx}: {issue_data.get('description', '')[:50]}...")
                    try:
                        issue_id = self._insert_issue(cursor, notice_id, issue_data, project_id)
                        logger.info(f"🔍 [DEBUG] _insert_issue 返回值: {issue_id}")
                        if issue_id:
                            imported_issues.append({
                                'id': issue_id,
                                'description': issue_data.get('description')
                            })
                        else:
                            logger.error(f"   ✗ 问题 {idx} 插入失败: _insert_issue 返回 None")
                            failed_issues.append({
                                'id': idx,
                                'description': issue_data.get('description')
                            })
                    except Exception as e:
                        logger.error(f"   ✗ 问题 {idx} 插入异常: {e}")
                        logger.error(f"   异常类型: {type(e).__name__}")
                        import traceback
                        logger.error(f"   异常堆栈:\n{traceback.format_exc()}")
                        failed_issues.append({
                            'id': idx,
                            'description': issue_data.get('description'),
                            'error': str(e)
                        })
                else:
                    logger.info(f"   ⊘ 跳过未选中的问题 {idx}")
                    skipped_issues.append(idx)

            logger.info(f"\n📊 导入统计:")
            logger.info(f"   成功导入: {len(imported_issues)} 个")
            logger.info(f"   导入失败: {len(failed_issues)} 个")
            logger.info(f"   跳过未选中: {len(skipped_issues)} 个")

            conn.commit()
            conn.close()

            if len(imported_issues) == 0:
                # 如果没有成功导入任何问题，返回失败信息
                logger.warning("⚠️ 成功导入 0 条记录，可能是一个问题。")
                return {
                    'success': False,
                    'error': '成功导入 0 条记录，请检查是否已选择问题或问题数据是否有效。',
                    'notice_number': notice_data['notice_number'],
                    'imported_issues_count': 0,
                    'failed_issues_count': len(failed_issues),
                    'failed_issues': failed_issues
                }

            return {
                'success': True,
                'notice_id': notice_id,
                'notice_number': notice_data['notice_number'],
                'imported_issues_count': len(imported_issues),
                'imported_issues': imported_issues,
                'failed_issues_count': len(failed_issues),
                'failed_issues': failed_issues
            }

        except Exception as e:
            logger.error(f"❌ 导入过程中发生错误: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }

    def _insert_supervision_notice_from_data(self, cursor, notice_data: Dict) -> Optional[int]:
        """
        从识别数据插入监督通知书

        Args:
            cursor: 数据库游标
            notice_data: 通知书数据

        Returns:
            通知书 ID
        """
        try:
            cursor.execute("""
                INSERT INTO supervision_notices
                (notice_number, check_date, check_unit, check_personnel, inspection_basis)
                VALUES (?, ?, ?, ?, ?)
            """, (
                notice_data['notice_number'],
                notice_data.get('check_date'),
                notice_data.get('check_unit'),
                notice_data.get('check_personnel'),
                notice_data.get('inspection_basis')
            ))

            return cursor.lastrowid

        except Exception as e:
            print(f"❌ 插入监督通知书失败: {e}")
            return None

    def _insert_project_from_data(self, cursor, notice_data: Dict) -> Optional[Dict]:
        """
        从识别数据插入项目

        Args:
            cursor: 数据库游标
            notice_data: 通知书数据

        Returns:
            项目信息字典
        """
        try:
            project_name = notice_data.get('project_name') or '未知项目'
            builder_unit = notice_data.get('builder_unit')

            # 使用匹配器进行项目匹配
            matcher = ProjectSectionMatcher(self.db_path)
            match_result = matcher.match_project(project_name)

            if match_result['status'] == 'error':
                print(f"❌ 项目匹配失败: {match_result['message']}")
                return None

            # 如果是完全匹配或相近匹配，直接返回
            if match_result['status'] in ['exact', 'similar']:
                return {
                    'id': match_result['project_id'],
                    'name': match_result['project_name'],
                    'status': match_result['status']
                }

            # 如果是新项目，插入数据库
            if match_result['status'] == 'new':
                cursor.execute("""
                    INSERT INTO projects
                    (project_name, builder_unit)
                    VALUES (?, ?)
                """, (
                    project_name,
                    builder_unit
                ))

                project_id = cursor.lastrowid
                return {
                    'id': project_id,
                    'name': project_name,
                    'status': 'new'
                }

        except Exception as e:
            print(f"❌ 插入项目失败: {e}")
            return None

