"""
导入服务模块
处理 Word 文档导入和数据存储
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from ..parsers.word_parser import parse_word_document
from .project_section_matcher import ProjectSectionMatcher
from .issue_category_classifier import IssueCategoryClassifier


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
                print(f"❌ 项目匹配失败: {match_result['message']}")
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
            print(f"❌ 插入项目失败: {e}")
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
            print(f"❌ 插入监督通知书失败: {e}")
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
            # 获取或创建标段
            section_code = issue.get('section_code') or '未知标段'
            section_name = issue.get('section_name')

            # 使用匹配器进行标段匹配
            matcher = ProjectSectionMatcher(self.db_path)
            match_result = matcher.match_section(project_id, section_code, section_name)

            if match_result['status'] == 'error':
                print(f"⚠️ 标段匹配失败: {match_result['message']}")
                # 继续处理，使用原始标段编号
                section_id = None
                # 使用 match_result 中的 section_name（如果原始为 None，则使用 section_code）
                section_name = match_result.get('section_name') or section_code
            elif match_result['status'] in ['exact', 'similar']:
                # 完全匹配或相近匹配
                section_id = match_result['section_id']
                # 使用 match_result 中的 section_name
                section_name = match_result.get('section_name')
            else:
                # 新标段，需要插入
                section_id = None
                # 使用 match_result 中的 section_name（如果原始为 None，则使用 section_code）
                section_name = match_result.get('section_name') or section_code

            # 如果没有找到匹配的标段，则创建新标段
            if section_id is None:
                try:
                    # 先尝试查询是否已存在相同的标段（可能是由于匹配器未能识别）
                    cursor.execute("""
                        SELECT id FROM sections
                        WHERE project_id = ? AND section_name = ?
                    """, (project_id, section_name))
                    existing_section = cursor.fetchone()

                    if existing_section:
                        # 标段已存在，使用现有的 section_id
                        section_id = existing_section[0]
                        print(f"✓ 标段已存在，使用现有标段 ID: {section_id}")
                    else:
                        # 标段不存在，创建新标段
                        cursor.execute("""
                            INSERT INTO sections
                            (project_id, section_code, section_name, contractor_unit, supervisor_unit)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            project_id,
                            section_code,
                            section_name,
                            issue.get('contractor'),
                            issue.get('supervisor')
                        ))
                        section_id = cursor.lastrowid
                        print(f"✓ 创建新标段，ID: {section_id}")
                except sqlite3.IntegrityError as e:
                    # 如果因为唯一性约束失败，查询现有的标段
                    print(f"⚠️ 标段插入失败（唯一性约束）: {e}")
                    cursor.execute("""
                        SELECT id FROM sections
                        WHERE project_id = ? AND section_name = ?
                    """, (project_id, section_name))
                    existing_section = cursor.fetchone()
                    if existing_section:
                        section_id = existing_section[0]
                        print(f"✓ 使用现有标段 ID: {section_id}")
                    else:
                        raise

            # 生成问题编号（临时）
            issue_number = f"ISSUE_{notice_id}_{datetime.now().timestamp()}"

            # 使用本地时间戳而不是 SQLite 的 UTC 时间戳
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 使用分类器自动识别问题类别
            issue_category = IssueCategoryClassifier.classify(
                description=issue['description'],
                site_name=issue.get('site_name'),
                section_name=issue.get('section_name')
            )

            # 如果分类器无法识别，默认设为施工安全
            if not issue_category or issue_category == '其它':
                issue_category = '施工安全'

            cursor.execute("""
                INSERT INTO issues
                (issue_number, supervision_notice_id, section_id, site_name, description,
                 is_rectification_notice, is_bad_behavior_notice, document_section, document_source,
                 severity, issue_category, inspection_unit, inspection_date, inspection_personnel,
                 rectification_requirements, rectification_deadline, responsible_unit,
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                issue_number,
                notice_id,
                section_id,
                issue.get('site_name'),
                issue['description'],
                issue['is_rectification_notice'],
                issue.get('is_bad_behavior_notice', False),
                issue['document_section'],
                'word',
                3,  # 默认等级为 3
                issue_category,  # 使用分类器识别的分类
                issue.get('inspection_unit'),
                issue.get('inspection_date'),
                issue.get('inspection_personnel'),
                issue.get('rectification_requirements'),
                issue.get('rectification_deadline'),
                issue.get('responsible_unit'),
                now,
                now
            ))

            return cursor.lastrowid

        except Exception as e:
            print(f"❌ 插入隐患问题失败: {e}")
            print(f"   问题数据: {issue}")
            print(f"   通知书 ID: {notice_id}, 项目 ID: {project_id}")
            import traceback
            traceback.print_exc()
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
            print(f"\n📋 开始导入选中的问题")
            print(f"   选中的问题 ID 列表: {selected_issue_ids}")
            print(f"   选中的问题数量: {len(selected_issue_ids)}")
            print(f"   通知书中的总问题数: {len(notice_data.get('issues', []))}")

            # 调试：打印前 3 个问题的 ID
            issues_list = notice_data.get('issues', [])
            if issues_list:
                print(f"   前 3 个问题的 ID:")
                for i, issue in enumerate(issues_list[:3]):
                    print(f"      问题 {i}: id={issue.get('id')}, description={issue.get('description', '')[:50]}")
            else:
                print(f"   ⚠️ 警告：notice_data 中没有 issues 字段！")
                print(f"   notice_data 的键: {list(notice_data.keys())}")

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
            if not notice_id:
                conn.close()
                return {
                    'success': False,
                    'error': '通知书插入失败'
                }

            # 3. 插入项目
            project_result = self._insert_project_from_data(cursor, notice_data)
            if not project_result:
                conn.close()
                return {
                    'success': False,
                    'error': '项目插入失败'
                }

            project_id = project_result['id']

            # 4. 导入选中的问题
            imported_issues = []
            skipped_issues = []
            failed_issues = []

            for idx, issue_data in enumerate(notice_data.get('issues', [])):
                issue_id_in_data = issue_data.get('id')
                print(f"   检查问题 {idx}: id={issue_id_in_data}, in selected={issue_id_in_data in selected_issue_ids}")

                if issue_id_in_data in selected_issue_ids:
                    print(f"   ✓ 导入问题 {idx}: {issue_id_in_data}")
                    issue_id = self._insert_issue(cursor, notice_id, issue_data, project_id)
                    if issue_id:
                        imported_issues.append({
                            'id': issue_id,
                            'description': issue_data.get('description')
                        })
                    else:
                        print(f"   ✗ 问题 {idx} ({issue_id_in_data}) 插入失败")
                        failed_issues.append({
                            'id': issue_id_in_data,
                            'description': issue_data.get('description')
                        })
                else:
                    skipped_issues.append(issue_id_in_data)

            print(f"\n📊 导入统计:")
            print(f"   成功导入: {len(imported_issues)} 个")
            print(f"   导入失败: {len(failed_issues)} 个")
            print(f"   跳过未选中: {len(skipped_issues)} 个")

            conn.commit()
            conn.close()

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
            print(f"❌ 导入过程中发生错误: {e}")
            import traceback
            traceback.print_exc()
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

