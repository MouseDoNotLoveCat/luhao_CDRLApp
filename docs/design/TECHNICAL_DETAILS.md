# 技术细节说明

## 问题 1: 时间戳问题的深入分析

### SQLite 时间戳行为

SQLite 的 `DEFAULT CURRENT_TIMESTAMP` 有以下特点：

1. **使用 UTC 时间**: 不是本地时间
2. **格式**: `YYYY-MM-DD HH:MM:SS` (UTC)
3. **时区问题**: 如果系统时区是 UTC+8（中国），则显示的时间会比本地时间早 8 小时

### 示例

假设当前本地时间是 **下午 5:03** (17:03)：
- 本地时间: `2025-11-05 17:03:08`
- UTC 时间: `2025-11-05 09:03:08`

如果使用 SQLite 的 `DEFAULT CURRENT_TIMESTAMP`，数据库中会存储 UTC 时间 `09:03:08`，显示为上午。

### 解决方案

显式使用 Python 的 `datetime.now()` 获取本地时间：

```python
from datetime import datetime

# 获取本地时间
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 在 INSERT 语句中显式设置
cursor.execute("""
    INSERT INTO issues (..., created_at, updated_at)
    VALUES (..., ?, ?)
""", (..., now, now))
```

---

## 问题 2: 点击事件处理的改进

### Element Plus 表格事件

Element Plus 的 `el-table` 组件提供了多个事件：

| 事件 | 触发条件 | 备注 |
|------|--------|------|
| `@row-click` | 点击行 | 如果行中有按钮，可能不会触发 |
| `@cell-click` | 点击单元格 | 更可靠，会传递行和列信息 |
| `@header-click` | 点击表头 | 用于排序等 |

### 为什么 @row-click 可能不工作

在 Element Plus 中，如果表格行中有交互元素（如按钮），点击这些元素时 `@row-click` 事件可能不会触发。

### 改进方案

使用 `@cell-click` 事件，并检查点击的列：

```vue
<el-table
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

---

## 问题 3: 项目数据的正确流向

### 数据流分析

**导入前**:
```
Word 文档
  ↓
解析器 (word_parser.py)
  ↓
parse_result = {
  'project_name': '黄百铁路广西段',
  'builder_unit': '云桂铁路广西有限责任公司',
  'rectification_notices': [...],
  'other_issues': [...]
}
```

**导入后（修复前）**:
```
parse_result
  ↓
_insert_issue() 方法
  ↓
尝试从 issue.get('project_name') 获取项目名称
  ↓
issue 对象中没有 project_name 字段
  ↓
默认为 '未知项目'
  ↓
projects 表中插入 '未知项目'
```

**导入后（修复后）**:
```
parse_result
  ↓
_insert_project() 方法
  ↓
从 parse_result.get('project_name') 获取项目名称
  ↓
projects 表中插入 '黄百铁路广西段'
  ↓
返回 project_id
  ↓
_insert_issue() 方法
  ↓
使用 project_id 创建标段和问题
```

### 关键改进

1. **分离关注点**: 项目信息从通知书级别提取，不依赖问题级别的数据
2. **数据一致性**: 所有问题都关联到同一个项目
3. **避免重复**: 检查项目是否已存在，避免重复插入

---

## 代码修改总结

### 修改 1: 添加 _insert_project 方法

```python
def _insert_project(self, cursor, parse_result: Dict) -> Optional[int]:
    """从通知书级别的数据插入项目"""
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
        INSERT INTO projects (project_name, builder_unit)
        VALUES (?, ?)
    """, (project_name, builder_unit))
    
    return cursor.lastrowid
```

### 修改 2: 修改导入流程

```python
# 在 import_word_document 方法中
project_id = self._insert_project(cursor, parse_result)

for issue in parse_result['rectification_notices']:
    issue_id = self._insert_issue(cursor, notice_id, issue, project_id)
```

### 修改 3: 修改 _insert_issue 签名

```python
def _insert_issue(self, cursor, notice_id: int, issue: Dict, project_id: int) -> Optional[int]:
    # 不再创建项目，直接使用 project_id
```

---

## 测试验证

所有修复都已通过以下测试：

✅ 后端 API 返回正确的项目信息
✅ 数据库中 projects 表显示正确的项目名称和建设单位
✅ 时间戳显示为本地时间（下午）
✅ 前端点击问题行可以跳转到详情页面


