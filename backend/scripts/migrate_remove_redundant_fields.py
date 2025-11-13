#!/usr/bin/env python3
"""
数据库迁移脚本：删除冗余的问题类别字段

功能：
1. 删除 issue_subcategory 字段（与 issue_type_level1 重复）
2. 删除 issue_type_level3 字段（未使用）

注意：SQLite 不支持 ALTER TABLE DROP COLUMN，所以使用重建表的方式

执行方式：
    python backend/scripts/migrate_remove_redundant_fields.py
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

        # 0. 清理之前失败的临时表和删除依赖的视图
        print("\n0️⃣ 清理环境...")
        cursor.execute("DROP TABLE IF EXISTS issues_new")
        cursor.execute("DROP VIEW IF EXISTS v_issues_summary")
        cursor.execute("DROP VIEW IF EXISTS v_rectification_progress")
        cursor.execute("DROP VIEW IF EXISTS v_rectification_notices_summary")
        cursor.execute("DROP VIEW IF EXISTS v_issues_by_type")
        print("   ✅ 环境清理成功")

        # 1. 获取当前表结构
        print("\n1️⃣ 获取当前表结构...")
        cursor.execute("PRAGMA table_info(issues)")
        columns = cursor.fetchall()
        print(f"   当前字段数: {len(columns)}")

        # 2. 创建临时表（不包含要删除的字段）
        print("\n2️⃣ 创建临时表...")
        cursor.execute("""
            CREATE TABLE issues_new (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              issue_number VARCHAR(100) UNIQUE NOT NULL,
              supervision_notice_id INTEGER NOT NULL,
              section_id INTEGER NOT NULL,
              site_name VARCHAR(200),
              issue_category VARCHAR(50),
              issue_type_level1 VARCHAR(100),
              issue_type_level2 VARCHAR(100),
              description TEXT NOT NULL,
              severity INTEGER DEFAULT 3,
              keywords VARCHAR(500),
              inspection_unit VARCHAR(100),
              inspection_date DATE,
              inspection_personnel VARCHAR(500),
              rectification_requirements TEXT,
              rectification_deadline DATE,
              rectification_date DATE,
              rectification_status VARCHAR(50),
              closure_date DATE,
              closure_status VARCHAR(50),
              closure_personnel VARCHAR(100),
              is_rectification_notice BOOLEAN DEFAULT FALSE,
              is_bad_behavior_notice BOOLEAN DEFAULT FALSE,
              responsible_unit VARCHAR(100),
              document_section VARCHAR(50),
              document_source VARCHAR(50),
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (supervision_notice_id) REFERENCES supervision_notices(id),
              FOREIGN KEY (section_id) REFERENCES sections(id)
            )
        """)
        print("   ✅ 临时表创建成功")

        # 3. 复制数据（不包含要删除的字段）
        print("\n3️⃣ 复制数据到临时表...")
        cursor.execute("""
            INSERT INTO issues_new (
              id, issue_number, supervision_notice_id, section_id, site_name,
              issue_category, issue_type_level1, issue_type_level2, description,
              severity, keywords, inspection_unit, inspection_date, inspection_personnel,
              rectification_requirements, rectification_deadline, rectification_date,
              rectification_status, closure_date, closure_status, closure_personnel,
              is_rectification_notice, is_bad_behavior_notice, responsible_unit,
              document_section, document_source, created_at, updated_at
            )
            SELECT
              id, issue_number, supervision_notice_id, section_id, site_name,
              issue_category, issue_type_level1, issue_type_level2, description,
              severity, keywords, inspection_unit, inspection_date, inspection_personnel,
              rectification_requirements, rectification_deadline, rectification_date,
              rectification_status, closure_date, closure_status, closure_personnel,
              is_rectification_notice, is_bad_behavior_notice, responsible_unit,
              document_section, document_source, created_at, updated_at
            FROM issues
        """)
        print(f"   ✅ 数据复制成功")

        # 4. 删除原表
        print("\n4️⃣ 删除原表...")
        cursor.execute("DROP TABLE issues")
        print("   ✅ 原表删除成功")

        # 5. 重命名临时表
        print("\n5️⃣ 重命名临时表...")
        cursor.execute("ALTER TABLE issues_new RENAME TO issues")
        print("   ✅ 表重命名成功")

        # 6. 重建索引
        print("\n6️⃣ 重建索引...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_issues_issue_number
              ON issues(issue_number)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_issues_supervision_notice_id
              ON issues(supervision_notice_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_issues_section_id
              ON issues(section_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_issues_site_name
              ON issues(site_name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_issues_issue_category
              ON issues(issue_category)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_issues_severity
              ON issues(severity)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_issues_inspection_date
              ON issues(inspection_date)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_issues_rectification_deadline
              ON issues(rectification_deadline)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_issues_rectification_date
              ON issues(rectification_date)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_issues_rectification_status
              ON issues(rectification_status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_issues_closure_date
              ON issues(closure_date)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_issues_closure_status
              ON issues(closure_status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_issues_is_rectification_notice
              ON issues(is_rectification_notice)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_issues_document_section
              ON issues(document_section)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_issues_document_source
              ON issues(document_source)
        """)
        print("   ✅ 索引重建成功")

        # 7. 重建视图
        print("\n7️⃣ 重建视图...")
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS v_issues_summary AS
            SELECT
              s.notice_number,
              s.check_date,
              s.check_unit,
              COUNT(i.id) as total_issues,
              SUM(CASE WHEN i.issue_category = '质量' THEN 1 ELSE 0 END) as quality_count,
              SUM(CASE WHEN i.issue_category = '安全' THEN 1 ELSE 0 END) as safety_count,
              SUM(CASE WHEN i.issue_category = '管理' THEN 1 ELSE 0 END) as management_count
            FROM supervision_notices s
            LEFT JOIN issues i ON s.id = i.supervision_notice_id
            GROUP BY s.id
        """)
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS v_rectification_progress AS
            SELECT
              i.issue_number,
              i.description,
              i.rectification_deadline,
              i.rectification_date,
              i.rectification_status,
              CASE
                WHEN i.rectification_date IS NULL THEN '未整改'
                WHEN i.rectification_date <= i.rectification_deadline THEN '按期完成'
                ELSE '逾期完成'
              END as status
            FROM issues i
            WHERE i.rectification_deadline IS NOT NULL
        """)
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS v_rectification_notices_summary AS
            SELECT
              s.notice_number,
              s.check_date,
              s.check_unit,
              COUNT(CASE WHEN i.is_rectification_notice = TRUE THEN 1 END) as rectification_notice_count,
              COUNT(CASE WHEN i.is_rectification_notice = FALSE THEN 1 END) as other_issues_count,
              COUNT(i.id) as total_issues
            FROM supervision_notices s
            LEFT JOIN issues i ON s.id = i.supervision_notice_id
            GROUP BY s.id
        """)
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS v_issues_by_type AS
            SELECT
              i.issue_number,
              i.description,
              i.site_name,
              i.issue_category,
              i.issue_type_level1,
              i.issue_type_level2,
              i.is_rectification_notice,
              i.is_bad_behavior_notice,
              i.document_section,
              i.document_source,
              i.severity,
              i.rectification_deadline,
              i.rectification_status
            FROM issues i
            ORDER BY i.is_rectification_notice DESC, i.severity DESC
        """)
        print("   ✅ 视图重建成功")

        # 8. 提交事务
        conn.commit()

        # 9. 验证
        print("\n8️⃣ 验证迁移结果...")
        cursor.execute("PRAGMA table_info(issues)")
        new_columns = cursor.fetchall()
        print(f"   新字段数: {len(new_columns)}")
        print(f"   删除字段数: {len(columns) - len(new_columns)}")

        # 显示新的字段列表
        print("\n   新的字段列表:")
        for col in new_columns:
            print(f"   - {col[1]} ({col[2]})")

        print("\n" + "=" * 60)
        print("✅ 迁移完成！")
        print(f"   - 删除了 issue_subcategory 字段")
        print(f"   - 删除了 issue_type_level3 字段")
        print(f"   - 保留了 issue_category、issue_type_level1、issue_type_level2 字段")
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
    print("🔄 问题类别字段优化 - 数据库迁移脚本")
    print("=" * 60)
    print(f"\n📍 数据库路径: {DB_PATH}")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    success = migrate()

    if success:
        print("\n✅ 迁移成功！")
        print("\n📝 后续步骤:")
        print("   1. 测试前端功能")
        print("   2. 测试后端 API")
        print("   3. 测试导入功能")
        print("   4. 验证过滤和统计功能")
    else:
        print("\n❌ 迁移失败！")
        print("   请检查错误信息并重试")

