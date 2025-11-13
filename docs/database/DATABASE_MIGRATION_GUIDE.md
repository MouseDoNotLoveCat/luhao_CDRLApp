# 🔄 数据库迁移指南

**版本**: 2.1  
**更新时间**: 2025-10-24  
**说明**: 从 v2.0 迁移到 v2.1（添加新字段）

---

## 📋 迁移内容

### 新增字段

在 `issues` 表中添加以下字段：

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| inspection_date | DATE | NULL | 检查日期 |
| inspection_personnel | VARCHAR(500) | NULL | 检查人员 |
| rectification_requirements | TEXT | NULL | 整改要求 |
| rectification_deadline | DATE | NULL | 整改期限 |
| rectification_date | DATE | NULL | 整改完成日期 |
| rectification_status | VARCHAR(50) | NULL | 整改状态 |
| closure_date | DATE | NULL | 销号日期 |
| closure_status | VARCHAR(50) | NULL | 销号状态 |
| closure_personnel | VARCHAR(100) | NULL | 销号人员 |

### 新增索引

```sql
CREATE INDEX idx_issues_inspection_date ON issues(inspection_date);
CREATE INDEX idx_issues_rectification_deadline ON issues(rectification_deadline);
CREATE INDEX idx_issues_rectification_date ON issues(rectification_date);
CREATE INDEX idx_issues_rectification_status ON issues(rectification_status);
CREATE INDEX idx_issues_closure_date ON issues(closure_date);
CREATE INDEX idx_issues_closure_status ON issues(closure_status);
```

---

## 🚀 迁移步骤

### 方法 1：完全重建（推荐用于新项目）

```bash
# 1. 备份旧数据库
cp backend/cdrl.db backend/cdrl.db.backup

# 2. 删除旧数据库
rm backend/cdrl.db

# 3. 使用新 schema 初始化数据库
python backend/scripts/init_db.py

# 4. 导入数据（如需要）
python backend/scripts/import_documents_v2.py
```

### 方法 2：增量迁移（用于已有数据的项目）

```bash
# 1. 备份数据库
cp backend/cdrl.db backend/cdrl.db.backup

# 2. 执行迁移脚本
python backend/scripts/migrate_v2_to_v2_1.py
```

---

## 📝 迁移脚本示例

### migrate_v2_to_v2_1.py

```python
#!/usr/bin/env python3
"""
数据库迁移脚本：v2.0 → v2.1
添加新字段到 issues 表
"""

import sqlite3
from pathlib import Path

def migrate_database(db_path: str):
    """执行数据库迁移"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("开始数据库迁移...")
        
        # 1. 添加新字段
        print("添加新字段...")
        
        new_fields = [
            ("inspection_date", "DATE"),
            ("inspection_personnel", "VARCHAR(500)"),
            ("rectification_requirements", "TEXT"),
            ("rectification_deadline", "DATE"),
            ("rectification_date", "DATE"),
            ("rectification_status", "VARCHAR(50)"),
            ("closure_date", "DATE"),
            ("closure_status", "VARCHAR(50)"),
            ("closure_personnel", "VARCHAR(100)"),
        ]
        
        for field_name, field_type in new_fields:
            try:
                cursor.execute(f"""
                    ALTER TABLE issues 
                    ADD COLUMN {field_name} {field_type}
                """)
                print(f"  ✅ 添加字段: {field_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"  ⚠️  字段已存在: {field_name}")
                else:
                    raise
        
        conn.commit()
        
        # 2. 创建新索引
        print("\n创建新索引...")
        
        indexes = [
            ("idx_issues_inspection_date", "inspection_date"),
            ("idx_issues_rectification_deadline", "rectification_deadline"),
            ("idx_issues_rectification_date", "rectification_date"),
            ("idx_issues_rectification_status", "rectification_status"),
            ("idx_issues_closure_date", "closure_date"),
            ("idx_issues_closure_status", "closure_status"),
        ]
        
        for index_name, column_name in indexes:
            try:
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS {index_name}
                    ON issues({column_name})
                """)
                print(f"  ✅ 创建索引: {index_name}")
            except sqlite3.OperationalError as e:
                print(f"  ⚠️  索引创建失败: {index_name}")
        
        conn.commit()
        
        print("\n✅ 数据库迁移完成！")
        
        # 3. 验证
        print("\n验证迁移结果...")
        cursor.execute("PRAGMA table_info(issues)")
        columns = cursor.fetchall()
        print(f"  issues 表现在有 {len(columns)} 个字段")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()


if __name__ == '__main__':
    db_path = Path("backend/cdrl.db")
    
    if not db_path.exists():
        print(f"❌ 数据库不存在: {db_path}")
    else:
        migrate_database(str(db_path))
```

---

## ✅ 迁移检查清单

迁移前：
- [ ] 备份原数据库
- [ ] 停止应用服务
- [ ] 确认数据库路径正确

迁移中：
- [ ] 执行迁移脚本
- [ ] 检查是否有错误

迁移后：
- [ ] 验证新字段已添加
- [ ] 验证索引已创建
- [ ] 测试应用功能
- [ ] 确认数据完整性

---

## 🔍 验证迁移

### 检查新字段

```bash
sqlite3 backend/cdrl.db "PRAGMA table_info(issues);"
```

### 检查新索引

```bash
sqlite3 backend/cdrl.db "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='issues';"
```

### 查询示例

```bash
sqlite3 backend/cdrl.db << 'EOF'
SELECT 
  issue_number,
  inspection_date,
  rectification_deadline,
  rectification_status,
  closure_status
FROM issues
LIMIT 5;
EOF
```

---

## 🆘 故障排除

### 问题 1：字段已存在

**症状**：迁移时出现 "duplicate column name" 错误

**解决**：这是正常的，说明字段已经存在，可以忽略

### 问题 2：索引创建失败

**症状**：索引创建时出现错误

**解决**：检查索引名称是否已存在，使用 `CREATE INDEX IF NOT EXISTS`

### 问题 3：数据库锁定

**症状**：迁移时出现 "database is locked" 错误

**解决**：
1. 确保没有其他进程访问数据库
2. 停止应用服务
3. 重试迁移

---

## 📚 相关文档

- `DATABASE_STRUCTURE_DETAILED.md` - 数据库详细设计
- `FIELD_MAPPING_GUIDE.md` - 字段映射指南
- `QUICK_REFERENCE_V2.md` - 快速参考


