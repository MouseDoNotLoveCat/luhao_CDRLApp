#!/usr/bin/env python3
"""
测试检查人员和检查依据提取功能
"""

import sys
import sqlite3
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.app.parsers.word_parser import WordDocumentParser
from backend.app.services.import_service import ImportService

def clear_database(db_path: str):
    """清空数据库"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 删除所有表中的数据
    cursor.execute("DELETE FROM issue_images")
    cursor.execute("DELETE FROM responsibility_units")
    cursor.execute("DELETE FROM issue_penalties")
    cursor.execute("DELETE FROM issues")
    cursor.execute("DELETE FROM sections")
    cursor.execute("DELETE FROM projects")
    cursor.execute("DELETE FROM supervision_notices")
    
    conn.commit()
    conn.close()
    print("✅ 数据库已清空")

def test_parser(file_path: str):
    """测试解析器"""
    print(f"\n📄 测试文件: {Path(file_path).name}")
    print("=" * 120)
    
    parser = WordDocumentParser(file_path)
    result = parser.parse()
    
    if result.get('status') == 'error':
        print(f"❌ 解析失败: {result.get('error')}")
        return None
    
    print(f"✅ 解析成功")
    print(f"   通知书编号: {result.get('notice_number')}")
    print(f"   检查日期: {result.get('check_date')}")
    print(f"   检查单位: {result.get('check_unit')}")
    print(f"   检查人员: {result.get('check_personnel')}")
    print(f"   检查依据: {result.get('inspection_basis')}")
    print(f"   识别问题: {result.get('total_issues')} 个")
    
    return result

def test_import(db_path: str, file_path: str):
    """测试导入"""
    print(f"\n📥 导入文件: {Path(file_path).name}")
    print("=" * 120)
    
    service = ImportService(db_path)
    import_result = service.import_word_document(file_path)
    
    if not import_result.get('success'):
        print(f"❌ 导入失败: {import_result.get('error')}")
        return None
    
    print(f"✅ 导入成功")
    print(f"   通知书编号: {import_result.get('notice_number')}")
    print(f"   下发整改通知单: {import_result.get('rectification_notices')} 个")
    print(f"   其它问题: {import_result.get('other_issues')} 个")
    print(f"   总计: {import_result.get('total_issues')} 个")
    
    return import_result

def verify_database(db_path: str):
    """验证数据库中的数据"""
    print(f"\n📊 数据库验证")
    print("=" * 120)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询所有监督通知书
    cursor.execute("""
        SELECT id, notice_number, check_personnel, inspection_basis
        FROM supervision_notices
        ORDER BY id
    """)
    
    notices = cursor.fetchall()
    
    for notice_id, notice_number, check_personnel, inspection_basis in notices:
        print(f"\n【{notice_number}】")
        print(f"   检查人员: {check_personnel}")
        print(f"   检查依据: {inspection_basis[:100] if inspection_basis else '(无)'}")
        
        # 查询该通知书下的问题数
        cursor.execute(
            "SELECT COUNT(*) FROM issues WHERE supervision_notice_id = ?",
            (notice_id,)
        )
        issue_count = cursor.fetchone()[0]
        print(f"   问题数: {issue_count} 个")
    
    conn.close()

def main():
    """主函数"""
    print("\n" + "=" * 120)
    print("✅ 检查人员和检查依据提取功能测试")
    print("=" * 120)
    
    # 数据库路径
    db_path = './backend/cdrl.db'
    
    # 测试文件
    test_files = [
        './Samples/黄百铁路9月监督通知书（2025-11号）(1).docx',
        './Samples/柳梧铁路内部监督通知书（编号：南宁站[2025]（通知）柳梧10号）.docx',
    ]
    
    # 清空数据库
    print("\n🗑️  清空数据库...")
    clear_database(db_path)
    
    # 测试解析
    print("\n🔍 测试解析器...")
    parse_results = []
    for file_path in test_files:
        if Path(file_path).exists():
            result = test_parser(file_path)
            if result:
                parse_results.append(result)
    
    # 测试导入
    print("\n📥 测试导入...")
    for file_path in test_files:
        if Path(file_path).exists():
            test_import(db_path, file_path)
    
    # 验证数据库
    verify_database(db_path)
    
    # 总结
    print("\n" + "=" * 120)
    print("✅ 测试完成")
    print("=" * 120)

if __name__ == '__main__':
    main()

