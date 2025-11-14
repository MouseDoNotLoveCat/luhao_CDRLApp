# 导入功能 - 标段重复插入问题修复

## 问题诊断

**症状**：
- 预期导入 84 个问题
- 实际只导入了 27 个问题
- 导入结果显示 `imported_issues_count: 27`，`failed_issues_count: 57`

**根本原因**：
1. `sections` 表有 `UNIQUE(project_id, section_name)` 约束
2. 当多个问题有相同的 `section_name` 时：
   - 第一个问题成功创建标段
   - 后续问题尝试插入相同的标段时，因为唯一性约束而失败
3. 异常被捕获但没有正确处理，导致问题插入失败

## 修复方案

### 修改文件：`backend/app/services/import_service.py`

在 `_insert_issue` 方法中（第 273-314 行），修改标段创建逻辑：

**修复前**：
```python
if section_id is None:
    cursor.execute("""
        INSERT INTO sections
        (project_id, section_code, section_name, contractor_unit, supervisor_unit)
        VALUES (?, ?, ?, ?, ?)
    """, (...))
    section_id = cursor.lastrowid
```

**修复后**：
```python
if section_id is None:
    try:
        # 先查询是否已存在相同的标段
        cursor.execute("""
            SELECT id FROM sections 
            WHERE project_id = ? AND section_name = ?
        """, (project_id, section_name))
        existing_section = cursor.fetchone()
        
        if existing_section:
            # 标段已存在，使用现有的 section_id
            section_id = existing_section[0]
        else:
            # 标段不存在，创建新标段
            cursor.execute("""
                INSERT INTO sections
                (project_id, section_code, section_name, contractor_unit, supervisor_unit)
                VALUES (?, ?, ?, ?, ?)
            """, (...))
            section_id = cursor.lastrowid
    except sqlite3.IntegrityError as e:
        # 如果因为唯一性约束失败，查询现有的标段
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

## 修复原理

1. **双重检查**：先查询是否存在，再尝试插入
2. **异常处理**：捕获 `IntegrityError`，然后查询现有的标段
3. **确保 section_id**：无论是新建还是现有，都能获得有效的 `section_id`

## 预期结果

✅ 所有 84 个问题都能成功导入到数据库
✅ 相同标段的问题共享同一个 `section_id`
✅ 导入结果显示 `imported_issues_count: 84`，`failed_issues_count: 0`

## 测试步骤

1. 启动应用：`./start-dev.sh`
2. 上传 Word 文档（84 个问题）
3. 选择全部问题
4. 点击"下一步"和"确认导入"
5. 验证导入结果显示 84 个问题成功导入
6. 查看数据库确认所有问题都已保存

## Git 提交

```bash
git add backend/app/services/import_service.py
git commit -m "fix: Handle duplicate section insertion with UNIQUE constraint"
```

