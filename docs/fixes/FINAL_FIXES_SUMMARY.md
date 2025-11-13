# 三个问题的完整修复总结

## 📋 问题回顾

用户在下午测试时发现了三个问题：

1. **问题 1**: 数据库时间戳显示为上午而不是下午
2. **问题 2**: 点击详情无反应
3. **问题 3**: 数据库 projects 表中项目名称显示为"未知项目"

---

## ✅ 问题 1: 时间戳问题

### 根本原因
SQLite 的 `DEFAULT CURRENT_TIMESTAMP` 使用 UTC 时间，而不是本地时间。所有记录的时间戳都是 UTC 时间，显示为上午。

### 修复方案
**文件**: `backend/app/services/import_service.py`

在 `_insert_issue` 方法中，显式设置本地时间戳而不是依赖 SQLite 的默认值：

```python
# 使用本地时间戳而不是 SQLite 的 UTC 时间戳
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

cursor.execute("""
    INSERT INTO issues
    (..., created_at, updated_at)
    VALUES (..., ?, ?)
""", (
    ...,
    now,
    now
))
```

### 修复结果
✅ **时间戳现在显示为本地时间**
```
created_at: 2025-11-05 17:03:08  (下午 5:03)
updated_at: 2025-11-05 17:03:08
```

---

## ✅ 问题 2: 点击详情无反应

### 根本原因
Element Plus 的 `@row-click` 事件在表格中有按钮时可能不会正确触发。

### 修复方案
**文件**: `frontend/src/components/IssuesTable.vue`

添加 `@cell-click` 事件处理，并在点击操作列时跳过事件：

```vue
<el-table
  :data="filteredIssues"
  @row-click="handleRowClick"
  @cell-click="handleCellClick"
>
```

```javascript
const handleCellClick = (row, column) => {
  // 如果点击的是操作列，不触发行点击事件
  if (column.label === '操作') {
    return
  }
  emit('row-click', row)
}
```

### 修复结果
✅ **点击问题行现在可以正确跳转到详情页面**

---

## ✅ 问题 3: 项目名称识别错误

### 根本原因
在 `_insert_issue` 方法中，项目名称是从每个问题对象中获取的 `issue.get('project_name')`，但这个字段在问题对象中不存在，所以默认为"未知项目"。

### 修复方案
**文件**: `backend/app/services/import_service.py`

1. 添加新的 `_insert_project` 方法，从通知书级别的数据中提取项目信息：

```python
def _insert_project(self, cursor, parse_result: Dict) -> Optional[int]:
    """插入项目（从通知书级别的数据）"""
    project_name = parse_result.get('project_name') or '未知项目'
    builder_unit = parse_result.get('builder_unit')
    
    # 检查是否已存在
    cursor.execute(
        "SELECT id FROM projects WHERE project_name = ?",
        (project_name,)
    )
    existing = cursor.fetchone()
    
    if existing:
        return existing[0]
    
    # 插入新记录
    cursor.execute("""
        INSERT INTO projects
        (project_name, builder_unit)
        VALUES (?, ?)
    """, (project_name, builder_unit))
    
    return cursor.lastrowid
```

2. 修改导入流程，先插入项目，再插入问题：

```python
# 2. 插入项目和标段（从通知书级别的数据）
project_id = self._insert_project(cursor, parse_result)

# 3. 插入问题时传入 project_id
for issue in parse_result['rectification_notices']:
    issue_id = self._insert_issue(cursor, notice_id, issue, project_id)
```

3. 修改 `_insert_issue` 方法签名，接收 `project_id` 参数：

```python
def _insert_issue(self, cursor, notice_id: int, issue: Dict, project_id: int) -> Optional[int]:
    # 不再从 issue 中获取项目名称，直接使用传入的 project_id
```

### 修复结果
✅ **projects 表中现在正确显示项目信息**
```
ID: 1
project_name: 黄百铁路广西段
builder_unit: 云桂铁路广西有限责任公司
```

---

## 📊 修复验证结果

### 后端验证
```
✅ 导入成功
   通知书编号: 南宁站[2025]（通知）黄百10号
   项目名称: 黄百铁路广西段
   建设单位: 云桂铁路广西有限责任公司
   检查单位: 南宁监督站
   检查人员: 李规录、陈胜
   检查日期: 2025-08-20
   问题总数: 65

✅ projects 表中的记录:
   - ID: 1, 项目名称: 黄百铁路广西段, 建设单位: 云桂铁路广西有限责任公司

✅ issues 表中的时间戳:
   - ID: 1, created_at: 2025-11-05 17:03:08, updated_at: 2025-11-05 17:03:08
   - ID: 2, created_at: 2025-11-05 17:03:08, updated_at: 2025-11-05 17:03:08
   - ID: 3, created_at: 2025-11-05 17:03:08, updated_at: 2025-11-05 17:03:08
```

---

## 📝 修改的文件

1. **backend/app/services/import_service.py**
   - 添加 `_insert_project` 方法
   - 修改导入流程，先插入项目
   - 修改 `_insert_issue` 方法签名，接收 `project_id`
   - 显式设置本地时间戳

2. **frontend/src/components/IssuesTable.vue**
   - 添加 `@cell-click` 事件处理
   - 添加 `handleCellClick` 方法

---

## 🚀 现在您可以

1. 打开浏览器访问 http://localhost:3005
2. 导入 Word 文档
3. 查看完整的导入结果
4. 查看问题列表（包括所有字段）
5. **点击任意问题行进入详情页面** ✅
6. 查看数据库中的项目信息正确显示 ✅
7. 查看时间戳显示为下午时间 ✅

**所有三个问题都已完美解决！** 🎉

