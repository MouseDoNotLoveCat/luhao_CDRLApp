# 项目名称冲突问题修复

## 问题描述

### 现象
在导入文档时，如果识别到的项目名称在数据库中已存在，系统会报错"导入失败（项目名冲突）"，而不是自动关联到现有项目。

### 具体场景
1. 导入文件：`柳梧铁路内部监督通知书（编号：南宁站[2026]（通知）柳梧1号）.docx`
2. 识别结果：项目名称被正确识别为"柳梧铁路"
3. 用户操作：在导入确认界面，没有修改项目名称，直接点击"确认导入"
4. 错误现象：系统提示"导入失败（项目名冲突）"
5. 数据库状态：`projects` 表中已经存在"柳梧铁路"这个项目

### 预期行为
当识别到的项目名称在数据库中已存在时，应该自动关联到现有项目，而不是报错。

## 问题根源

### 数据库约束
`projects` 表的 `project_name` 字段有 `UNIQUE` 约束：

```sql
CREATE TABLE projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_name VARCHAR(200) NOT NULL UNIQUE,  -- 唯一约束
  builder_unit VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 代码问题
在 `backend/app/services/import_service.py` 的 `import_selected_issues()` 方法中（第 620-636 行），代码逻辑如下：

**修复前的代码**：
```python
# 3.1 创建或获取项目
project_id = None
if project_info.get('project_id'):
    # 使用现有项目
    project_id = project_info['project_id']
    logger.info(f"   使用现有项目 ID: {project_id}")
else:
    # 创建新项目
    project_name = project_info.get('project_name', '未知项目')
    builder_unit = project_info.get('builder_unit', '')

    cursor.execute(
        "INSERT INTO projects (project_name, builder_unit) VALUES (?, ?)",
        (project_name, builder_unit)
    )
    project_id = cursor.lastrowid
    logger.info(f"   创建新项目 ID: {project_id}, 名称: {project_name}")
```

**问题分析**：
- 当 `project_info` 中没有 `project_id` 时（即用户没有在前端选择现有项目），代码直接执行 `INSERT INTO projects`
- 如果项目名称已存在，由于 `UNIQUE` 约束，会导致 SQL 错误
- 错误被捕获后返回"项目名冲突"错误

## 修复方案

### 修复逻辑
在创建新项目之前，先检查项目名称是否已存在：
1. 如果项目名称已存在，使用现有项目的 ID
2. 如果项目名称不存在，才创建新项目

### 修复后的代码
```python
# 3.1 创建或获取项目
project_id = None
if project_info.get('project_id'):
    # 使用现有项目（用户在前端选择了现有项目）
    project_id = project_info['project_id']
    logger.info(f"   使用现有项目 ID: {project_id}")
else:
    # 需要创建新项目或查找现有项目
    project_name = project_info.get('project_name', '未知项目')
    builder_unit = project_info.get('builder_unit', '')

    # 先检查项目名称是否已存在
    cursor.execute(
        "SELECT id FROM projects WHERE project_name = ?",
        (project_name,)
    )
    existing_project = cursor.fetchone()

    if existing_project:
        # 项目已存在，使用现有项目
        project_id = existing_project[0]
        logger.info(f"   项目已存在，使用现有项目 ID: {project_id}, 名称: {project_name}")
    else:
        # 项目不存在，创建新项目
        cursor.execute(
            "INSERT INTO projects (project_name, builder_unit) VALUES (?, ?)",
            (project_name, builder_unit)
        )
        project_id = cursor.lastrowid
        logger.info(f"   创建新项目 ID: {project_id}, 名称: {project_name}")
```

## 修复效果

### 场景 1：项目名称已存在
- **操作**：导入文档，识别到项目名称"柳梧铁路"（数据库中已存在）
- **结果**：自动关联到现有的"柳梧铁路"项目，导入成功
- **日志**：`项目已存在，使用现有项目 ID: X, 名称: 柳梧铁路`

### 场景 2：项目名称不存在
- **操作**：导入文档，识别到项目名称"新项目"（数据库中不存在）
- **结果**：创建新项目"新项目"，导入成功
- **日志**：`创建新项目 ID: Y, 名称: 新项目`

### 场景 3：用户在前端选择了现有项目
- **操作**：用户在导入确认界面手动选择了现有项目
- **结果**：使用用户选择的项目 ID，导入成功
- **日志**：`使用现有项目 ID: Z`

## 测试建议

### 测试步骤
1. **测试项目名称已存在的情况**：
   - 确保数据库中已有"柳梧铁路"项目
   - 导入柳梧铁路监督通知书
   - 在导入确认界面不修改项目名称，直接点击"确认导入"
   - 验证导入成功，问题关联到现有的"柳梧铁路"项目

2. **测试项目名称不存在的情况**：
   - 导入一个新项目的监督通知书（如"测试铁路"）
   - 在导入确认界面不修改项目名称，直接点击"确认导入"
   - 验证导入成功，自动创建了"测试铁路"项目

3. **测试用户手动选择现有项目**：
   - 导入文档，识别到项目名称"项目A"
   - 在导入确认界面，用户手动选择现有项目"项目B"
   - 点击"确认导入"
   - 验证导入成功，问题关联到用户选择的"项目B"

4. **测试批量修改项目**：
   - 导入包含多个标段的文档
   - 使用批量修改功能为多个标段设置相同的项目
   - 验证导入成功，所有标段的问题都关联到正确的项目

## 相关文件

- **修复文件**：`backend/app/services/import_service.py`
- **修复位置**：`import_selected_issues()` 方法，第 620-649 行
- **数据库表**：`projects` 表
- **前端组件**：
  - `frontend/src/components/ImportConfirm.vue` - 导入确认界面
  - `frontend/src/components/ProjectSelectionDialog.vue` - 项目选择对话框
  - `frontend/src/stores/importStore.js` - 导入状态管理

## 注意事项

1. **建设单位字段**：当项目已存在时，不会更新建设单位字段。如果需要更新，需要额外的逻辑处理。

2. **项目名称大小写**：SQLite 的字符串比较默认是大小写敏感的。如果需要大小写不敏感的比较，需要使用 `COLLATE NOCASE`。

3. **并发问题**：在高并发场景下，可能存在竞态条件。建议使用事务和适当的锁机制。

4. **日志记录**：修复后的代码会在日志中明确记录是使用了现有项目还是创建了新项目，便于调试和追踪。

