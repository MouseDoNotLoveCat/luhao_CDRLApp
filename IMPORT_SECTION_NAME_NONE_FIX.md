# 导入功能 - section_name 为 None 导致导入失败修复

## 问题诊断

**症状**：
- 应用修复后（commit 4f48e0e），测试导入功能
- 导入结果显示 0 个问题成功导入
- `sections` 表和 `issues` 表中没有任何数据

**根本原因**：
在修复标段重复插入问题时，我使用了原始的 `section_name` 变量进行查询。但当 `section_name` 为 `None` 时：
1. `ProjectSectionMatcher.match_section()` 返回 `section_name: section_code`（第 154 行）
2. 但我的修复代码仍然使用原始的 `section_name = None`
3. 查询 `WHERE project_id = ? AND section_name = ?` 时，`section_name = None` 导致查询失败
4. 异常被捕获，问题插入失败

## 修复方案

### 修改文件
`backend/app/services/import_service.py` - `_insert_issue` 方法（第 253-320 行）

### 修复逻辑
在处理 `match_result` 时，始终使用 `match_result` 中的 `section_name`，而不是原始的 `section_name` 变量：

```python
if match_result['status'] == 'error':
    section_id = None
    # 使用 match_result 中的 section_name
    section_name = match_result.get('section_name') or section_code
elif match_result['status'] in ['exact', 'similar']:
    section_id = match_result['section_id']
    # 使用 match_result 中的 section_name
    section_name = match_result.get('section_name')
else:
    # 新标段
    section_id = None
    # 使用 match_result 中的 section_name
    section_name = match_result.get('section_name') or section_code
```

## 修复原理

1. **确保 section_name 不为 None**：从 `match_result` 获取的 `section_name` 总是有值
2. **一致性**：所有代码路径都使用相同的 `section_name` 来查询和插入
3. **容错性**：如果 `match_result` 中的 `section_name` 为 None，则使用 `section_code` 作为备选

## 预期结果

✅ 所有 84 个问题都能成功导入到数据库
✅ `sections` 表包含标段数据
✅ `issues` 表包含 84 条问题记录
✅ 导入结果显示 `imported_issues_count: 84`

## Git 提交

```
58e5ba1 - fix: Use section_name from match_result to handle None values
```

## 测试步骤

1. 启动应用：`./start-dev.sh`
2. 清空数据库中的 `sections` 和 `issues` 表
3. 上传 Word 文档（84 个问题）
4. 选择全部问题并确认导入
5. 验证导入结果显示 84 个问题成功导入

