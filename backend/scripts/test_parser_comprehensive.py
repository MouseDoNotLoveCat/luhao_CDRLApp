#!/usr/bin/env python3
"""
综合测试脚本 - 测试改进后的解析器
1. 清空数据库
2. 解析并导入4个关键测试文件
3. 导出详细的解析结果
4. 提供测试统计
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.parsers.word_parser import WordDocumentParser, parse_word_document


def clear_database(db_path):
    """清空数据库中的所有数据"""
    print("\n" + "=" * 120)
    print("🗑️  清空数据库")
    print("=" * 120)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        # 删除所有表中的数据
        for table in tables:
            table_name = table[0]
            cursor.execute(f"DELETE FROM {table_name}")
            print(f"✅ 清空表: {table_name}")
        
        conn.commit()
        conn.close()
        print("\n✅ 数据库清空完成")
        return True
    except Exception as e:
        print(f"❌ 清空数据库失败: {e}")
        return False


def parse_and_import_files(db_path, test_files):
    """解析并导入测试文件"""
    print("\n" + "=" * 120)
    print("📥 解析并导入测试文件")
    print("=" * 120)

    results = []

    for file_path in test_files:
        if not Path(file_path).exists():
            print(f"❌ 文件不存在: {file_path}")
            continue

        print(f"\n📄 处理: {Path(file_path).name}")

        # 解析文件
        parser = WordDocumentParser(file_path)
        parse_result = parser.parse()

        # 导入到数据库
        import_result = _import_document(db_path, file_path, parse_result)

        results.append({
            'file_path': file_path,
            'file_name': Path(file_path).name,
            'parse_result': parse_result,
            'import_result': import_result
        })

        if import_result['success']:
            print(f"✅ 导入成功")
            print(f"   - 下发整改通知单问题: {import_result['rectification_notices']}")
            print(f"   - 其它问题: {import_result['other_issues']}")
            print(f"   - 总计: {import_result['total_issues']}")
        else:
            print(f"❌ 导入失败: {import_result.get('error')}")

    return results


def _import_document(db_path: str, file_path: str, parse_result: dict) -> dict:
    """导入单个文档到数据库"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 1. 插入或获取项目
        project_name = parse_result.get('project_name') or '未知项目'
        cursor.execute("SELECT id FROM projects WHERE project_name = ?", (project_name,))
        project_row = cursor.fetchone()

        if project_row:
            project_id = project_row[0]
        else:
            cursor.execute("INSERT INTO projects (project_name) VALUES (?)", (project_name,))
            conn.commit()
            project_id = cursor.lastrowid

        # 2. 插入监督通知书
        cursor.execute("""
            INSERT INTO supervision_notices
            (notice_number, check_date, check_unit, check_personnel)
            VALUES (?, ?, ?, ?)
        """, (
            parse_result['notice_number'],
            parse_result['check_date'],
            parse_result['check_unit'],
            parse_result['check_personnel']
        ))
        conn.commit()
        notice_id = cursor.lastrowid

        # 3. 处理所有问题
        rectification_count = 0
        other_count = 0

        for issue in parse_result.get('rectification_notices', []):
            if _insert_issue(cursor, conn, project_id, notice_id, issue):
                rectification_count += 1

        for issue in parse_result.get('other_issues', []):
            if _insert_issue(cursor, conn, project_id, notice_id, issue):
                other_count += 1

        conn.close()

        return {
            'success': True,
            'file_name': Path(file_path).name,
            'notice_number': parse_result['notice_number'],
            'rectification_notices': rectification_count,
            'other_issues': other_count,
            'total_issues': rectification_count + other_count
        }
    except Exception as e:
        return {
            'success': False,
            'file_name': Path(file_path).name,
            'error': str(e)
        }


def _insert_issue(cursor, conn, project_id: int, notice_id: int, issue: dict) -> bool:
    """插入问题到数据库"""
    try:
        section_code = issue.get('section_code')
        site_name = issue.get('site_name')

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
                (project_id, section_code, section_name, contractor_unit, supervisor_unit)
                VALUES (?, ?, ?, ?, ?)
            """, (
                project_id,
                section_code,
                issue.get('section_name'),
                issue.get('contractor'),
                issue.get('supervisor')
            ))
            conn.commit()
            section_id = cursor.lastrowid

        # 插入问题
        issue_number = f"{issue.get('section_code', 'UNKNOWN')}-{site_name}-{datetime.now().timestamp()}"
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
            1 if issue.get('is_rectification_notice') else 0,
            1 if issue.get('is_bad_behavior_notice') else 0,
            issue.get('document_section', 'other'),
            'word',
            3,
            '施工安全',
            issue.get('inspection_unit'),
            issue.get('inspection_personnel'),
            issue.get('inspection_date')
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ 插入问题失败: {e}")
        return False


def export_detailed_results(db_path, results):
    """导出详细的解析结果"""
    print("\n" + "=" * 120)
    print("📊 详细解析结果")
    print("=" * 120)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for result in results:
        file_name = result['file_name']
        parse_result = result['parse_result']
        
        print(f"\n{'=' * 120}")
        print(f"📄 {file_name}")
        print(f"{'=' * 120}")
        
        # 基本信息
        print(f"\n【基本信息】")
        print(f"  项目名称: {parse_result.get('project_name', '未知')}")
        print(f"  建设单位: {parse_result.get('builder_unit', '未知')}")
        print(f"  通知书编号: {parse_result.get('notice_number', '未知')}")
        print(f"  检查日期: {parse_result.get('check_date', '未知')}")
        print(f"  检查单位: {parse_result.get('check_unit', '未知')}")
        print(f"  检查人员: {parse_result.get('check_personnel', '未知')}")
        
        # 文档结构
        print(f"\n【文档结构】")
        print(f"  结构类型: {parse_result.get('document_structure', '未知')}")
        print(f"  下发整改通知单问题数: {len(parse_result.get('rectification_notices', []))}")
        print(f"  其它问题数: {len(parse_result.get('other_issues', []))}")
        print(f"  总计: {parse_result.get('total_issues', 0)}")
        
        # 文档声明的问题数
        declared_count = parse_result.get('declared_issues_count')
        if declared_count:
            actual_count = parse_result.get('total_issues', 0)
            match = "✅" if declared_count == actual_count else "⚠️"
            print(f"  文档声明: {declared_count} 个问题 {match}")
        
        # 详细问题列表
        print(f"\n【详细问题列表】")
        
        # 查询数据库中的问题
        notice_number = parse_result.get('notice_number')
        cursor.execute("""
            SELECT s.section_code, s.section_name, i.site_name, i.description
            FROM issues i
            JOIN sections s ON i.section_id = s.id
            WHERE i.supervision_notice_id = (
                SELECT id FROM supervision_notices WHERE notice_number = ?
            )
            ORDER BY s.section_code, i.site_name
        """, (notice_number,))
        
        issues = cursor.fetchall()
        
        if not issues:
            print("  (无问题记录)")
        else:
            current_section = None
            current_site = None
            count = 0
            
            for section_code, section_name, site_name, description in issues:
                if section_code != current_section or site_name != current_site:
                    if current_section is not None:
                        print()
                    current_section = section_code
                    current_site = site_name
                    print(f"\n  【{section_code}】{section_name}")
                    print(f"    工点: {site_name}")
                    count = 0
                
                count += 1
                desc_short = description[:80] if description else ""
                print(f"      {count}. {desc_short}")
    
    conn.close()


def print_test_statistics(results):
    """打印测试统计"""
    print("\n" + "=" * 120)
    print("📈 测试统计")
    print("=" * 120)

    print(f"\n【导入结果统计】")
    print(f"{'文件名':<50} {'识别':<8} {'声明':<8} {'状态':<8}")
    print("-" * 120)

    total_files = len(results)
    complete_match = 0

    for result in results:
        file_name = Path(result['file_name']).name[:48]
        parse_result = result['parse_result']

        actual = parse_result.get('total_issues', 0)
        declared_info = parse_result.get('declared_issues_count')

        # 处理 declared_issues_count 可能是字典的情况
        if isinstance(declared_info, dict):
            declared = declared_info.get('total')
        else:
            declared = declared_info

        if declared and actual == declared:
            status = "✅ 完全匹配"
            complete_match += 1
        elif declared:
            status = f"⚠️  差异: {actual - declared:+d}"
        else:
            status = "❓ 无声明"

        print(f"{file_name:<50} {actual:<8} {declared or '-':<8} {status:<8}")

    print("-" * 120)
    if total_files > 0:
        print(f"总计: {total_files} 个文件, {complete_match} 个完全匹配 ({complete_match*100//total_files}%)")
    else:
        print(f"总计: {total_files} 个文件")


if __name__ == "__main__":
    # 配置
    db_path = Path(__file__).parent.parent / "cdrl.db"
    test_files = [
        "./Samples/20250730玉岑内部监督通知书（编号：南宁站〔2025〕（通知）玉岑08号）.docx",
        "./Samples/柳梧铁路内部监督通知书（编号：南宁站[2025]（通知）柳梧10号）.docx",
        "./Samples/柳梧铁路内部监督通知书（编号：南宁站[2025]（通知）柳梧6号）-1.docx",
        "./Samples/黄百铁路9月监督通知书（2025-11号）(1).docx",
    ]
    
    # 执行测试
    if clear_database(str(db_path)):
        results = parse_and_import_files(str(db_path), test_files)
        export_detailed_results(str(db_path), results)
        print_test_statistics(results)
        
        print("\n" + "=" * 120)
        print("✅ 测试完成")
        print("=" * 120)

