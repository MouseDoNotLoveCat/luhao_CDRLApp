# 🔧 问题类别字段优化 - 实施方案

## 📋 优化目标

从 5 个问题类别相关字段简化为 3 个，消除冗余，保持三层分类结构。

## 🎯 优化方案

### 保留的 3 个字段

```sql
issue_category VARCHAR(50)      -- 一级分类：工程质量/施工安全/管理行为/其它
issue_type_level1 VARCHAR(100)  -- 二级分类：混凝土工程、隧道施工等
issue_type_level2 VARCHAR(100)  -- 三级分类：原材料、洞口开挖等
```

### 删除的 2 个字段

```sql
issue_subcategory VARCHAR(50)   -- ❌ 删除（与 issue_type_level1 重复）
issue_type_level3 VARCHAR(100)  -- ❌ 删除（未使用，预留）
```

## 📝 修改清单

### 1. 数据库架构修改

**文件**: `database_schema.sql`

#### 修改 1.1：删除字段定义（第 62-67 行）
```sql
-- 修改前
issue_category VARCHAR(50),
issue_subcategory VARCHAR(50),
issue_type_level1 VARCHAR(100),
issue_type_level2 VARCHAR(100),
issue_type_level3 VARCHAR(100),

-- 修改后
issue_category VARCHAR(50),      -- 一级分类
issue_type_level1 VARCHAR(100),  -- 二级分类
issue_type_level2 VARCHAR(100),  -- 三级分类
```

#### 修改 1.2：删除索引（如果存在）
- 检查是否有 `idx_issues_issue_subcategory` 索引
- 检查是否有 `idx_issues_issue_type_level3` 索引

#### 修改 1.3：更新视图（第 307-322 行）
```sql
-- 修改前
CREATE VIEW IF NOT EXISTS v_issues_by_type AS
SELECT
  i.issue_number,
  i.description,
  i.site_name,
  i.issue_category,
  i.issue_subcategory,  -- ❌ 删除
  ...

-- 修改后
CREATE VIEW IF NOT EXISTS v_issues_by_type AS
SELECT
  i.issue_number,
  i.description,
  i.site_name,
  i.issue_category,
  i.issue_type_level1,
  i.issue_type_level2,
  ...
```

### 2. 后端 API 修改

**文件**: `backend/app/main.py`

#### 修改 2.1：/api/issues 端点（第 183-189 行）
```python
# 修改前
SELECT i.id, i.issue_number, i.description, i.is_rectification_notice,
       i.document_section, i.severity, i.site_name, i.issue_category,
       i.issue_type_level1, i.issue_type_level2, ...

# 修改后
SELECT i.id, i.issue_number, i.description, i.is_rectification_notice,
       i.document_section, i.severity, i.site_name, i.issue_category,
       i.issue_type_level1, i.issue_type_level2, ...
# （无需修改，已经不包含 issue_subcategory）
```

#### 修改 2.2：/api/notices/{notice_id} 端点（第 368-371 行）
```python
# 修改前
SELECT i.id, i.site_name, i.description, i.issue_category, 
       i.issue_type_level1, i.issue_type_level2, ...

# 修改后
SELECT i.id, i.site_name, i.description, i.issue_category, 
       i.issue_type_level1, i.issue_type_level2, ...
# （无需修改，已经不包含 issue_subcategory）
```

### 3. 前端组件修改

**文件**: `frontend/src/components/IssuesTable.vue`

#### 修改 3.1：删除 issue_subcategory 列
```vue
<!-- 修改前 -->
<el-table-column prop="issue_category" label="一级分类" width="100" />
<el-table-column prop="issue_subcategory" label="二级分类（旧）" width="120" />
<el-table-column prop="issue_type_level1" label="二级分类" width="120" />
<el-table-column prop="issue_type_level2" label="三级分类" width="120" />

<!-- 修改后 -->
<el-table-column prop="issue_category" label="一级分类" width="100" />
<el-table-column prop="issue_type_level1" label="二级分类" width="120" />
<el-table-column prop="issue_type_level2" label="三级分类" width="120" />
```

### 4. 数据库迁移脚本

**新建文件**: `backend/scripts/migrate_remove_redundant_fields.py`

```python
"""
迁移脚本：删除冗余的问题类别字段
- 删除 issue_subcategory 字段
- 删除 issue_type_level3 字段
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / 'cdrl.db'

def migrate():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # 删除 issue_subcategory 字段
        cursor.execute("""
            ALTER TABLE issues DROP COLUMN issue_subcategory
        """)
        print("✅ 删除 issue_subcategory 字段成功")
        
        # 删除 issue_type_level3 字段
        cursor.execute("""
            ALTER TABLE issues DROP COLUMN issue_type_level3
        """)
        print("✅ 删除 issue_type_level3 字段成功")
        
        conn.commit()
        print("✅ 迁移完成")
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
```

## 📊 修改影响总结

| 组件 | 修改内容 | 影响程度 |
|------|--------|--------|
| 数据库架构 | 删除 2 个字段 | 中 |
| 后端 API | 无需修改 | 无 |
| 前端表格 | 删除 1 列 | 低 |
| 导入功能 | 无需修改 | 无 |
| 分类器 | 无需修改 | 无 |
| 过滤功能 | 无需修改 | 无 |

## ✅ 实施步骤

1. ✅ 备份数据库
2. ⏳ 修改 `database_schema.sql`
3. ⏳ 修改 `backend/app/main.py`（如果需要）
4. ⏳ 修改 `frontend/src/components/IssuesTable.vue`
5. ⏳ 创建迁移脚本
6. ⏳ 执行迁移脚本
7. ⏳ 测试所有功能

---

**方案日期**: 2025-11-08  
**实施状态**: 待确认  
**风险等级**: 低

