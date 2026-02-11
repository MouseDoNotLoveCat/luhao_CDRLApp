#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看和清理数据库中的玉岑铁路数据
"""

import sqlite3
import sys

def view_recent_notices():
    """查看最近导入的通知书"""
    conn = sqlite3.connect('backend/cdrl.db')
    cursor = conn.cursor()
    
    # 查找最近的通知书
    cursor.execute('''
        SELECT id, notice_number, check_date, created_at
        FROM supervision_notices 
        ORDER BY created_at DESC
        LIMIT 10
    ''')
    
    notices = cursor.fetchall()
    print('=' * 80)
    print('最近导入的通知书：')
    print('=' * 80)
    
    for notice in notices:
        print(f'\nID: {notice[0]}')
        print(f'通知书编号: {notice[1]}')
        print(f'检查日期: {notice[2]}')
        print(f'导入时间: {notice[3]}')
        
        # 统计该通知书的问题数量
        cursor.execute('SELECT COUNT(*) FROM issues WHERE supervision_notice_id = ?', (notice[0],))
        count = cursor.fetchone()[0]
        print(f'问题数量: {count}')
        
        # 查看前3个问题的施工单位
        cursor.execute('''
            SELECT id, construction_unit, supervision_unit, description 
            FROM issues 
            WHERE supervision_notice_id = ? 
            ORDER BY id
            LIMIT 3
        ''', (notice[0],))
        issues = cursor.fetchall()
        
        if issues:
            print('前3个问题：')
            for issue in issues:
                desc = issue[3][:40] if issue[3] else ''
                if len(desc) > 40:
                    desc = desc[:37] + '...'
                print(f'  问题{issue[0]}: 施工={issue[1]}, 监理={issue[2]}')
                print(f'           描述={desc}')
        print('-' * 80)
    
    conn.close()

def delete_notice(notice_id):
    """删除指定的通知书及其所有问题"""
    conn = sqlite3.connect('backend/cdrl.db')
    cursor = conn.cursor()
    
    # 先查看要删除的通知书信息
    cursor.execute('SELECT notice_number FROM supervision_notices WHERE id = ?', (notice_id,))
    result = cursor.fetchone()
    
    if not result:
        print(f'错误：找不到 ID 为 {notice_id} 的通知书')
        conn.close()
        return
    
    notice_number = result[0]
    
    # 统计问题数量
    cursor.execute('SELECT COUNT(*) FROM issues WHERE supervision_notice_id = ?', (notice_id,))
    issue_count = cursor.fetchone()[0]
    
    print(f'\n准备删除：')
    print(f'  通知书 ID: {notice_id}')
    print(f'  通知书编号: {notice_number}')
    print(f'  关联问题数: {issue_count}')
    
    # 确认删除
    confirm = input('\n确认删除？(yes/no): ')
    if confirm.lower() != 'yes':
        print('已取消删除')
        conn.close()
        return
    
    # 删除问题
    cursor.execute('DELETE FROM issues WHERE supervision_notice_id = ?', (notice_id,))
    deleted_issues = cursor.rowcount
    
    # 删除通知书
    cursor.execute('DELETE FROM supervision_notices WHERE id = ?', (notice_id,))
    
    conn.commit()
    conn.close()
    
    print(f'\n✅ 删除成功！')
    print(f'  已删除 {deleted_issues} 个问题')
    print(f'  已删除通知书 {notice_number}')

def main():
    if len(sys.argv) == 1:
        # 没有参数，显示最近的通知书
        view_recent_notices()
        print('\n使用方法：')
        print('  查看通知书: python3 cleanup_data.py')
        print('  删除通知书: python3 cleanup_data.py delete <notice_id>')
    elif len(sys.argv) == 3 and sys.argv[1] == 'delete':
        # 删除指定的通知书
        try:
            notice_id = int(sys.argv[2])
            delete_notice(notice_id)
        except ValueError:
            print('错误：notice_id 必须是数字')
    else:
        print('使用方法：')
        print('  查看通知书: python3 cleanup_data.py')
        print('  删除通知书: python3 cleanup_data.py delete <notice_id>')

if __name__ == '__main__':
    main()

