#!/usr/bin/env python3
"""
数据库迁移脚本：为 sections 表添加 testing_unit 字段
"""

import sqlite3
from pathlib import Path

def migrate_add_testing_unit():
    """为 sections 表添加 testing_unit 字段"""
    
    # 获取数据库路径
    db_path = Path(__file__).parent.parent / "cdrl.db"
    
    if not db_path.exists():
        print(f"❌ 数据库不存在: {db_path}")
        return False
    
    try:
        # 连接数据库
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 检查 testing_unit 字段是否已存在
        cursor.execute("PRAGMA table_info(sections)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'testing_unit' in column_names:
            print("✅ testing_unit 字段已存在，无需迁移")
            conn.close()
            return True
        
        # 添加 testing_unit 字段
        print("🔄 正在添加 testing_unit 字段...")
        cursor.execute("""
            ALTER TABLE sections
            ADD COLUMN testing_unit VARCHAR(100)
        """)
        
        conn.commit()
        print("✅ testing_unit 字段添加成功")
        
        # 验证字段
        cursor.execute("PRAGMA table_info(sections)")
        columns = cursor.fetchall()
        print("✅ sections 表结构:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        return False

if __name__ == "__main__":
    migrate_add_testing_unit()

