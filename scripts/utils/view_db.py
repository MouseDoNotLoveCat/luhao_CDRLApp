#!/usr/bin/env python3
"""
快速查看 cdrl.db 数据库的脚本
"""

import sqlite3
from pathlib import Path

def view_database():
    """查看数据库"""
    db_path = Path("backend/cdrl.db")
    
    if not db_path.exists():
        print(f"❌ 数据库不存在: {db_path}")
        print("请先运行: python backend/scripts/init_db.py")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    print("\n" + "=" * 100)
    print("📊 CDRL 数据库数据查看")
    print("=" * 100)
    print()
    
    # 1. 监督通知书
    print("1️⃣  监督通知书")
    print("-" * 100)
    cursor.execute("""
        SELECT id, notice_number, check_date, check_unit
        FROM supervision_notices
        ORDER BY check_date DESC
    """)
    rows = cursor.fetchall()
    print(f"{'ID':<5} {'编号':<40} {'检查日期':<15} {'检查单位':<20}")
    print("-" * 100)
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<40} {row[2]:<15} {row[3]:<20}")
    print(f"\n总计: {len(rows)} 条\n")
    
    # 2. 统计信息
    print("2️⃣  统计信息")
    print("-" * 100)
    cursor.execute("""
        SELECT 
          COUNT(*) as 总数,
          SUM(CASE WHEN is_rectification_notice = 1 THEN 1 ELSE 0 END) as 下发整改,
          SUM(CASE WHEN is_rectification_notice = 0 THEN 1 ELSE 0 END) as 其它问题
        FROM issues
    """)
    row = cursor.fetchone()
    print(f"总问题数: {row[0]}")
    print(f"下发整改通知单: {row[1]}")
    print(f"其它问题: {row[2]}\n")
    
    # 3. 按通知书统计
    print("3️⃣  按通知书统计")
    print("-" * 100)
    cursor.execute("""
        SELECT 
          s.notice_number,
          COUNT(i.id) as 问题数,
          SUM(CASE WHEN i.is_rectification_notice = 1 THEN 1 ELSE 0 END) as 下发整改,
          SUM(CASE WHEN i.is_rectification_notice = 0 THEN 1 ELSE 0 END) as 其它问题
        FROM supervision_notices s
        LEFT JOIN issues i ON s.id = i.supervision_notice_id
        GROUP BY s.id
        ORDER BY COUNT(i.id) DESC
    """)
    rows = cursor.fetchall()
    print(f"{'通知书编号':<40} {'问题数':<10} {'下发整改':<10} {'其它问题':<10}")
    print("-" * 100)
    for row in rows:
        print(f"{row[0]:<40} {row[1]:<10} {row[2]:<10} {row[3]:<10}")
    print()
    
    # 4. 问题详情（前 10 条）
    print("4️⃣  问题详情（前 10 条）")
    print("-" * 100)
    cursor.execute("""
        SELECT id, issue_number, is_rectification_notice, SUBSTR(description, 1, 60) as 描述
        FROM issues
        LIMIT 10
    """)
    rows = cursor.fetchall()
    print(f"{'ID':<5} {'编号':<30} {'下发整改':<10} {'描述':<50}")
    print("-" * 100)
    for row in rows:
        status = "✅ 是" if row[2] == 1 else "❌ 否"
        print(f"{row[0]:<5} {row[1]:<30} {status:<10} {row[3]:<50}")
    print()
    
    # 5. 下发整改通知单的问题
    print("5️⃣  下发整改通知单的问题（前 5 条）")
    print("-" * 100)
    cursor.execute("""
        SELECT id, issue_number, SUBSTR(description, 1, 70) as 描述
        FROM issues
        WHERE is_rectification_notice = 1
        LIMIT 5
    """)
    rows = cursor.fetchall()
    print(f"{'ID':<5} {'编号':<30} {'描述':<60}")
    print("-" * 100)
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<30} {row[2]:<60}")
    print()
    
    # 6. 其它问题
    print("6️⃣  其它问题（前 5 条）")
    print("-" * 100)
    cursor.execute("""
        SELECT id, issue_number, SUBSTR(description, 1, 70) as 描述
        FROM issues
        WHERE is_rectification_notice = 0
        LIMIT 5
    """)
    rows = cursor.fetchall()
    print(f"{'ID':<5} {'编号':<30} {'描述':<60}")
    print("-" * 100)
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<30} {row[2]:<60}")
    print()
    
    print("=" * 100)
    print("✅ 数据查看完成")
    print("=" * 100)
    print()
    print("💡 提示:")
    print("  - 查看详细文档: VIEW_DATABASE_GUIDE.md 或 HOW_TO_VIEW_DATABASE.md")
    print("  - 启动 API 服务: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000")
    print("  - 使用 SQLite 命令行: sqlite3 backend/cdrl.db")
    print("  - 使用 DB Browser: https://sqlitebrowser.org/")
    print()
    
    conn.close()


if __name__ == "__main__":
    view_database()

