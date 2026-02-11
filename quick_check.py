#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('backend/cdrl.db')
cursor = conn.cursor()

# 检查 2026 年问题的关联情况
cursor.execute('''
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN i.section_id IS NULL THEN 1 ELSE 0 END) as no_section,
        SUM(CASE WHEN s.project_id IS NULL THEN 1 ELSE 0 END) as no_project
    FROM issues i
    LEFT JOIN sections s ON i.section_id = s.id
    WHERE i.inspection_date LIKE '%2026%'
''')
result = cursor.fetchone()
print(f"2026年问题统计:")
print(f"  总数: {result[0]}")
print(f"  没有section_id: {result[1]}")
print(f"  没有project_id: {result[2]}")
print()

# 查看样本数据
cursor.execute('''
    SELECT 
        i.id, i.section_name, i.section_id, 
        s.section_name as s_name, s.project_id,
        p.project_name
    FROM issues i
    LEFT JOIN sections s ON i.section_id = s.id
    LEFT JOIN projects p ON s.project_id = p.id
    WHERE i.inspection_date LIKE '%2026%'
    LIMIT 5
''')
print("样本数据:")
for row in cursor.fetchall():
    print(f"  ID:{row[0]} section_name:{row[1]} section_id:{row[2]} project_id:{row[4]} project:{row[5]}")

conn.close()

