#!/usr/bin/env python3
"""
数据库迁移脚本：添加 responsible_person 字段

功能：
1. 在 issues 表中添加 responsible_person 字段（整改责任人）

执行方式：
    python backend/scripts/migrate_add_responsible_person.py
"""

import sqlite3
from pathlib import Path
from datetime import datetime

# 获取数据库路径
DB_PATH = Path(__file__).parent.parent / 'cdrl.db'


def backup_database():
    """备份数据库"""
    import shutil
    backup_path = DB_PATH.with_suffix('.db.backup')
    shutil.copy(str(DB_PATH), str(backup_path))
    print(f"✅ 数据库备份完成: {backup_path}")
    return backup_path


def migrate():
    """执行迁移"""
    if not DB_PATH.exists():
        print(f"❌ 数据库文件不存在: {DB_PATH}")
        return False

    # 备份数据库
    backup_path = backup_database()

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    try:
        print("\n🔄 开始迁移...")
        print("=" * 60)

        # 1. 检查字段是否已存在
        print("\n1️⃣ 检查 responsible_person 字段...")
        cursor.execute("PRAGMA table_info(issues)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        if 'responsible_person' in column_names:
            print("   ⚠️ responsible_person 字段已存在，无需添加")
            conn.close()
            return True

        # 2. 添加字段
        print("\n2️⃣ 添加 responsible_person 字段...")
        cursor.execute("""
            ALTER TABLE issues
            ADD COLUMN responsible_person VARCHAR(100)
        """)
        print("   ✅ 字段添加成功")

        # 3. 提交事务
        conn.commit()

        # 4. 验证
        print("\n3️⃣ 验证迁移结果...")
        cursor.execute("PRAGMA table_info(issues)")
        new_columns = cursor.fetchall()
        new_column_names = [col[1] for col in new_columns]

        if 'responsible_person' in new_column_names:
            print("   ✅ responsible_person 字段已成功添加")
        else:
            print("   ❌ responsible_person 字段添加失败")
            return False

        print("\n" + "=" * 60)
        print("✅ 迁移完成！")
        print(f"   - 添加了 responsible_person 字段")
        print(f"\n💾 备份文件: {backup_path}")
        return True

    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        print("   正在回滚...")
        conn.rollback()
        return False

    finally:
        conn.close()


if __name__ == '__main__':
    print("=" * 60)
    print("🔄 添加 responsible_person 字段 - 数据库迁移脚本")
    print("=" * 60)
    print(f"\n📍 数据库路径: {DB_PATH}")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    success = migrate()

    if success:
        print("\n✅ 迁移成功！")
        print("\n📝 后续步骤:")
        print("   1. 重启后端服务")
        print("   2. 测试前端功能")
    else:
        print("\n❌ 迁移失败！")
        print("   请检查错误信息并重试")

