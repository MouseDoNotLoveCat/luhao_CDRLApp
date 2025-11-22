# 导入功能部分失败问题 - 根本原因和修复

## 问题概述

**症状**：
- 用户上传 Word 文档，系统识别出 84 个问题
- 用户选择全部 84 个问题并点击"确认导入"
- **预期**：84 个问题全部导入到数据库
- **实际**：只有 27 个问题成功导入，57 个问题导入失败

## 根本原因分析

### 数据库约束
```sql
CREATE TABLE sections (
  ...
  UNIQUE(project_id, section_name)
);
```

### 问题流程
1. **问题 1-27**：这些问题有不同的 `section_name`
   - 第一次遇到某个 `section_name` 时，创建新标段
   - 插入成功，问题导入成功

2. **问题 28-84**：这些问题有重复的 `section_name`
   - 尝试创建已存在的标段
   - 因为 `UNIQUE(project_id, section_name)` 约束，插入失败
   - 异常被捕获，问题导入失败

### 代码问题
```python
# 原始代码（第 273-286 行）
if section_id is None:
    cursor.execute("""
        INSERT INTO sections
        (project_id, section_code, section_name, contractor_unit, supervisor_unit)
        VALUES (?, ?, ?, ?, ?)
    """, (...))
    section_id = cursor.lastrowid
```

**问题**：没有处理 `IntegrityError` 异常，当插入失败时，`section_id` 仍为 `None`，导致后续问题插入失败。

## 修复方案

### 修改内容
在 `backend/app/services/import_service.py` 的 `_insert_issue` 方法中：

1. **先查询后插入**：在插入前先查询是否存在
2. **异常处理**：捕获 `IntegrityError`，然后查询现有标段
3. **确保 section_id**：无论哪种情况都能获得有效的 `section_id`

### 修复代码
```python
if section_id is None:
    try:
        # 先查询是否已存在
        cursor.execute("""
            SELECT id FROM sections 
            WHERE project_id = ? AND section_name = ?
        """, (project_id, section_name))
        existing_section = cursor.fetchone()
        
        if existing_section:
            section_id = existing_section[0]
        else:
            # 创建新标段
            cursor.execute("""
                INSERT INTO sections
                (project_id, section_code, section_name, contractor_unit, supervisor_unit)
                VALUES (?, ?, ?, ?, ?)
            """, (...))
            section_id = cursor.lastrowid
    except sqlite3.IntegrityError as e:
        # 处理唯一性约束冲突
        cursor.execute("""
            SELECT id FROM sections 
            WHERE project_id = ? AND section_name = ?
        """, (project_id, section_name))
        existing_section = cursor.fetchone()
        if existing_section:
            section_id = existing_section[0]
        else:
            raise
```

## 预期结果

✅ 所有 84 个问题都能成功导入
✅ 相同标段的问题共享同一个 `section_id`
✅ 导入结果显示 `imported_issues_count: 84`

## Git 提交

```
4f48e0e - fix: Handle duplicate section insertion with UNIQUE constraint
59f7427 - docs: Add section duplicate insertion fix documentation
```

## 下一步

请按照以下步骤测试修复：

1. 启动应用：`./start-dev.sh`
2. 上传包含 84 个问题的 Word 文档
3. 选择全部问题
4. 点击"下一步"和"确认导入"
5. 验证导入结果显示 84 个问题成功导入
6. 查看数据库确认所有问题都已保存

