#!/usr/bin/env python3
"""
数据库初始化脚本
"""

import sqlite3
import os
from pathlib import Path

def init_database():
    """初始化数据库"""
    
    # 获取数据库路径
    db_path = Path(__file__).parent.parent / "cdrl.db"
    
    # 读取 SQL 脚本
    sql_file = Path(__file__).parent.parent.parent / "database_schema.sql"
    
    if not sql_file.exists():
        print(f"❌ SQL 脚本不存在: {sql_file}")
        return False
    
    try:
        # 连接数据库
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 读取并执行 SQL 脚本
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # 执行脚本
        cursor.executescript(sql_script)
        conn.commit()
        
        print(f"✅ 数据库初始化成功: {db_path}")
        
        # 验证表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"✅ 创建了 {len(tables)} 个表:")
        for table in tables:
            print(f"   - {table[0]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

if __name__ == "__main__":
    init_database()

