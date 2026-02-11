#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复数据库中的项目名称
将"未知项目"改为"玉岑铁路"（根据标段名称 YCZQ 推断）
"""

import sqlite3

DB_PATH = 'backend/cdrl.db'

def fix_project_name():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("🔧 修复项目名称")
    print("=" * 60)
    print()
    
    # 1. 查看当前的项目
    cursor.execute('SELECT * FROM projects')
    print("当前 Projects 表:")
    for row in cursor.fetchall():
        print(f"  ID:{row[0]} 项目名:{row[1]} 建设单位:{row[2]}")
    print()
    
    # 2. 查看 ID=1 的项目关联的标段
    cursor.execute('SELECT section_name FROM sections WHERE project_id = 1 LIMIT 10')
    print("ID=1 项目关联的标段（前10个）:")
    for row in cursor.fetchall():
        print(f"  - {row[0]}")
    print()
    
    # 3. 根据标段名称推断项目名
    # YCZQ = 玉岑铁路
    # LWZF = 柳梧铁路
    # 等等
    
    print("🔍 分析标段名称...")
    cursor.execute('''
        SELECT section_name, COUNT(*) as cnt
        FROM sections
        WHERE project_id = 1
        GROUP BY SUBSTR(section_name, 1, 4)
        ORDER BY cnt DESC
    ''')
    print("标段前缀统计:")
    for row in cursor.fetchall():
        print(f"  {row[0][:4]}: {row[1]} 个标段")
    print()
    
    # 4. 更新项目名称
    new_project_name = "玉岑铁路"
    print(f"📝 将 ID=1 的项目名称更新为: {new_project_name}")
    
    cursor.execute('''
        UPDATE projects
        SET project_name = ?
        WHERE id = 1
    ''', (new_project_name,))
    
    conn.commit()
    
    # 5. 验证更新
    cursor.execute('SELECT * FROM projects WHERE id = 1')
    row = cursor.fetchone()
    print(f"✅ 更新后: ID:{row[0]} 项目名:{row[1]} 建设单位:{row[2]}")
    print()
    
    # 6. 检查影响的问题数量
    cursor.execute('''
        SELECT COUNT(*)
        FROM issues i
        JOIN sections s ON i.section_id = s.id
        WHERE s.project_id = 1
    ''')
    affected_count = cursor.fetchone()[0]
    print(f"📊 影响的问题数量: {affected_count} 条")
    
    conn.close()
    print()
    print("=" * 60)
    print("✅ 完成！")
    print("=" * 60)

if __name__ == '__main__':
    fix_project_name()

