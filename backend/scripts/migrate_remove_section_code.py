#!/usr/bin/env python3
"""
数据库迁移脚本：删除 section_code 字段，使用 section_name 作为唯一标识

此脚本安全地执行以下操作：
1. 检查 section_code 字段是否存在
2. 创建新的 sections 表（不包含 section_code）
3. 迁移现有数据
4. 删除旧表
5. 重命名新表
"""

import sqlite3
from pathlib import Path
import sys


def migrate_remove_section_code():
    """执行数据库迁移"""
    db_path = Path(__file__).parent.parent / "cdrl.db"
    
    if not db_path.exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 检查 section_code 字段是否存在
        cursor.execute("PRAGMA table_info(sections)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'section_code' not in column_names:
            print("✅ section_code 字段已不存在，无需迁移")
            conn.close()
            return True
        
        print("🔄 开始迁移数据库...")
        print("📋 当前表结构:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # 开始事务
        cursor.execute("BEGIN TRANSACTION")
        
        try:
            # 步骤 1: 创建新表（不包含 section_code）
            print("\n📝 步骤 1: 创建新表...")
            cursor.execute("""
                CREATE TABLE sections_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    section_name VARCHAR(200) NOT NULL,
                    contractor_unit VARCHAR(100),
                    supervisor_unit VARCHAR(100),
                    designer_unit VARCHAR(100),
                    testing_unit VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id),
                    UNIQUE(project_id, section_name)
                )
            """)
            print("   ✓ 新表创建成功")
            
            # 步骤 2: 迁移数据
            print("\n📝 步骤 2: 迁移数据...")
            cursor.execute("""
                INSERT INTO sections_new 
                (id, project_id, section_name, contractor_unit, supervisor_unit, designer_unit, testing_unit, created_at, updated_at)
                SELECT 
                    id, project_id, section_name, contractor_unit, supervisor_unit, designer_unit, testing_unit, created_at, updated_at
                FROM sections
            """)
            rows_migrated = cursor.rowcount
            print(f"   ✓ 已迁移 {rows_migrated} 条记录")
            
            # 步骤 3: 删除旧表
            print("\n📝 步骤 3: 删除旧表...")
            cursor.execute("DROP TABLE sections")
            print("   ✓ 旧表删除成功")
            
            # 步骤 4: 重命名新表
            print("\n📝 步骤 4: 重命名新表...")
            cursor.execute("ALTER TABLE sections_new RENAME TO sections")
            print("   ✓ 新表重命名成功")
            
            # 步骤 5: 重建索引
            print("\n📝 步骤 5: 重建索引...")
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sections_project_id
                ON sections(project_id)
            """)
            print("   ✓ 索引重建成功")
            
            # 提交事务
            conn.commit()
            print("\n✅ 数据库迁移完成！")
            
            # 验证
            print("\n📋 迁移后的表结构:")
            cursor.execute("PRAGMA table_info(sections)")
            columns = cursor.fetchall()
            for col in columns:
                print(f"   - {col[1]} ({col[2]})")
            
            # 验证数据
            cursor.execute("SELECT COUNT(*) FROM sections")
            count = cursor.fetchone()[0]
            print(f"\n📊 表中记录数: {count}")
            
            conn.close()
            return True
            
        except Exception as e:
            # 回滚事务
            cursor.execute("ROLLBACK")
            print(f"\n❌ 迁移失败: {str(e)}")
            conn.close()
            return False
    
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("数据库迁移脚本：删除 section_code 字段")
    print("=" * 60)
    
    success = migrate_remove_section_code()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ 迁移成功！")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ 迁移失败！")
        print("=" * 60)
        sys.exit(1)

