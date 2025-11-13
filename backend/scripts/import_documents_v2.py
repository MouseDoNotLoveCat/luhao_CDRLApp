#!/usr/bin/env python3
"""
导入监督通知书文档 - 版本 3
按照新的数据库结构导入（项目 -> 标段 -> 问题，问题包含工点名称）
"""

import sqlite3
from pathlib import Path
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.app.parsers.word_parser import parse_word_document

def import_document(db_path: str, file_path: str) -> bool:
    """导入单个文档"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 解析文件
        result = parse_word_document(file_path)

        if result['status'] != 'success':
            print(f"❌ 解析失败: {result.get('error')}")
            return False

        print(f"✅ 文件解析成功: {result['file_name']}")
        print(f"   编号: {result['notice_number']}")
        print(f"   项目: {result['project_name']}")

        # 显示警告信息（如果有）
        if result.get('warnings'):
            print()
            print("⚠️  警告信息:")
            for warning in result['warnings']:
                print(f"   - {warning}")

        print()

        # 1. 插入或获取项目
        project_name = result['project_name'] or '未知项目'
        cursor.execute(
            "SELECT id FROM projects WHERE project_name = ?",
            (project_name,)
        )
        project_row = cursor.fetchone()

        if project_row:
            project_id = project_row[0]
            print(f"   项目已存在: ID={project_id}")
        else:
            cursor.execute(
                "INSERT INTO projects (project_name) VALUES (?)",
                (project_name,)
            )
            conn.commit()
            project_id = cursor.lastrowid
            print(f"   创建新项目: ID={project_id}")

        # 2. 插入监督通知书
        cursor.execute("""
            INSERT INTO supervision_notices
            (notice_number, check_date, check_unit, check_personnel)
            VALUES (?, ?, ?, ?)
        """, (
            result['notice_number'],
            result['check_date'],
            result['check_unit'],
            result['check_personnel']
        ))
        conn.commit()
        notice_id = cursor.lastrowid
        print(f"   插入监督通知书: ID={notice_id}")
        print()

        # 3. 处理下发整改通知单的问题
        print(f"📝 处理下发整改通知单的问题: {len(result['rectification_notices'])} 个")

        for i, issue in enumerate(result['rectification_notices'], 1):
            section_code = issue.get('section_code')
            site_name = issue.get('site_name')
            contractor = issue.get('contractor')
            supervisor = issue.get('supervisor')

            # 获取或创建标段
            cursor.execute(
                "SELECT id FROM sections WHERE project_id = ? AND section_code = ?",
                (project_id, section_code)
            )
            section_row = cursor.fetchone()

            if section_row:
                section_id = section_row[0]
            else:
                cursor.execute("""
                    INSERT INTO sections
                    (project_id, section_code, contractor_unit, supervisor_unit)
                    VALUES (?, ?, ?, ?)
                """, (project_id, section_code, contractor, supervisor))
                conn.commit()
                section_id = cursor.lastrowid

            # 插入问题（不再创建工点记录，直接存储工点名称）
            issue_number = f"{result['notice_number']}-R{i}"
            cursor.execute("""
                INSERT INTO issues
                (issue_number, supervision_notice_id, section_id, site_name,
                 description, rectification_requirements, rectification_deadline,
                 responsible_unit, is_rectification_notice, is_bad_behavior_notice,
                 document_section, document_source, severity, issue_category,
                 inspection_unit, inspection_personnel, inspection_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                issue_number,
                notice_id,
                section_id,
                site_name,
                issue.get('description'),
                issue.get('rectification_requirements'),
                issue.get('rectification_deadline'),
                issue.get('responsible_unit'),
                1 if issue.get('is_rectification_notice') else 0,
                1 if issue.get('is_bad_behavior_notice') else 0,
                issue.get('document_section', 'rectification'),
                'word',
                3,  # 默认等级为 3
                '施工安全',  # 默认分类为施工安全
                issue.get('inspection_unit'),
                issue.get('inspection_personnel'),
                issue.get('inspection_date')
            ))
            conn.commit()
            print(f"   {i}. {issue_number} -> 标段: {section_code}, 工点: {site_name}")

        # 4. 处理其它问题
        print()
        print(f"📝 处理其它问题: {len(result['other_issues'])} 个")

        for i, issue in enumerate(result['other_issues'], 1):
            section_code = issue.get('section_code')
            site_name = issue.get('site_name')
            contractor = issue.get('contractor')
            supervisor = issue.get('supervisor')

            # 获取或创建标段
            cursor.execute(
                "SELECT id FROM sections WHERE project_id = ? AND section_code = ?",
                (project_id, section_code)
            )
            section_row = cursor.fetchone()

            if section_row:
                section_id = section_row[0]
            else:
                cursor.execute("""
                    INSERT INTO sections
                    (project_id, section_code, contractor_unit, supervisor_unit)
                    VALUES (?, ?, ?, ?)
                """, (project_id, section_code, contractor, supervisor))
                conn.commit()
                section_id = cursor.lastrowid

            # 插入问题
            issue_number = f"{result['notice_number']}-O{i}"
            cursor.execute("""
                INSERT INTO issues
                (issue_number, supervision_notice_id, section_id, site_name,
                 description, is_rectification_notice, is_bad_behavior_notice,
                 document_section, document_source, severity, issue_category,
                 inspection_unit, inspection_personnel, inspection_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                issue_number,
                notice_id,
                section_id,
                site_name,
                issue.get('description'),
                0,  # is_rectification_notice = False
                0,  # is_bad_behavior_notice = False
                issue.get('document_section', 'other'),
                'word',
                3,  # 默认等级为 3
                '施工安全',  # 默认分类为施工安全
                issue.get('inspection_unit'),
                issue.get('inspection_personnel'),
                issue.get('inspection_date')
            ))
            conn.commit()
            print(f"   {i}. {issue_number} -> 标段: {section_code}, 工点: {site_name}")

        print()
        print("=" * 80)
        print(f"✅ 导入完成: {len(result['rectification_notices']) + len(result['other_issues'])} 个问题")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"❌ 导入失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()


if __name__ == '__main__':
    db_path = Path("backend/cdrl.db")
    file_path = "Samples/柳梧铁路内部监督通知书（编号：南宁站[2025]（通知）柳梧6号）-1.docx"
    
    import_document(str(db_path), file_path)

