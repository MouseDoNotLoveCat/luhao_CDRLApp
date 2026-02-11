#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查项目名称关联情况"""

import sqlite3

conn = sqlite3.connect('backend/cdrl.db')
cursor = conn.cursor()

print('=' * 80)
print('📊 数据库关联情况检查')
print('=' * 80)
print()

# 1. 检查 issues 表中有多少记录有 section_id
cursor.execute('SELECT COUNT(*) FROM issues WHERE section_id IS NOT NULL')
issues_with_section = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM issues WHERE section_id IS NULL')
issues_without_section = cursor.fetchone()[0]

print('1️⃣ Issues 表中的 section_id 情况:')
print(f'   - 有 section_id: {issues_with_section} 条')
print(f'   - 无 section_id (NULL): {issues_without_section} 条')
print()

# 2. 检查 sections 表中有多少记录有 project_id
cursor.execute('SELECT COUNT(*) FROM sections WHERE project_id IS NOT NULL')
sections_with_project = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM sections WHERE project_id IS NULL')
sections_without_project = cursor.fetchone()[0]

print('2️⃣ Sections 表中的 project_id 情况:')
print(f'   - 有 project_id: {sections_with_project} 条')
print(f'   - 无 project_id (NULL): {sections_without_project} 条')
print()

# 3. 检查 projects 表总数
cursor.execute('SELECT COUNT(*) FROM projects')
total_projects = cursor.fetchone()[0]
print(f'3️⃣ Projects 表总记录数: {total_projects} 条')
print()

# 4. 检查 2026 年的问题是否有项目关联
cursor.execute('''
    SELECT 
        COUNT(*) as total,
        COUNT(s.project_id) as with_project,
        COUNT(*) - COUNT(s.project_id) as without_project
    FROM issues i
    LEFT JOIN sections s ON i.section_id = s.id
    WHERE i.inspection_date LIKE '%2026%'
''')
result = cursor.fetchone()
print('4️⃣ 2026年问题的项目关联情况:')
print(f'   - 总数: {result[0]} 条')
print(f'   - 有项目关联: {result[1]} 条')
print(f'   - 无项目关联: {result[2]} 条')
print()

# 5. 查看几条 2026 年问题的详细信息
cursor.execute('''
    SELECT 
        i.id,
        i.section_name,
        i.section_id,
        s.section_name as section_table_name,
        s.project_id,
        p.project_name
    FROM issues i
    LEFT JOIN sections s ON i.section_id = s.id
    LEFT JOIN projects p ON s.project_id = p.id
    WHERE i.inspection_date LIKE '%2026%'
    LIMIT 10
''')
print('5️⃣ 2026年问题样本数据（前10条）:')
print(f'   {"ID":<6} {"问题中标段名":<20} {"section_id":<12} {"sections表标段名":<20} {"project_id":<12} {"项目名"}')
print('   ' + '-' * 100)
for row in cursor.fetchall():
    print(f'   {row[0]:<6} {str(row[1] or "-"):<20} {str(row[2] or "NULL"):<12} {str(row[3] or "-"):<20} {str(row[4] or "NULL"):<12} {row[5] or "-"}')
print()

# 6. 查看 sections 表的数据
cursor.execute('SELECT id, section_name, project_id FROM sections LIMIT 10')
print('6️⃣ Sections 表样本数据（前10条）:')
print(f'   {"ID":<6} {"标段名":<30} {"project_id"}')
print('   ' + '-' * 60)
for row in cursor.fetchall():
    print(f'   {row[0]:<6} {row[1]:<30} {row[2] or "NULL"}')
print()

# 7. 查看 projects 表的数据
cursor.execute('SELECT id, project_name FROM projects LIMIT 10')
print('7️⃣ Projects 表样本数据（前10条）:')
print(f'   {"ID":<6} {"项目名"}')
print('   ' + '-' * 60)
for row in cursor.fetchall():
    print(f'   {row[0]:<6} {row[1]}')
print()

# 8. 检查 issues 表中 section_name 的值
cursor.execute('''
    SELECT DISTINCT section_name 
    FROM issues 
    WHERE inspection_date LIKE '%2026%' AND section_name IS NOT NULL
    LIMIT 10
''')
print('8️⃣ 2026年问题中的标段名称（去重，前10个）:')
for row in cursor.fetchall():
    print(f'   - {row[0]}')

conn.close()
print()
print('=' * 80)

