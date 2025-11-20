# 问题类别导入错误 - 代码变更详情

## 📝 修改文件列表

### 1. frontend/src/stores/importStore.js

**修改方法**：`importSelected`（第 464-509 行）

**修改前**：
```javascript
const noticeData = recognizedNotices.value[0]
const selectedIds = Array.from(selectedIssueIds.value).map(index => `temp_${index}`)
const result = await importService.importSelected(noticeData, selectedIds)
```

**修改后**：
```javascript
const noticeData = recognizedNotices.value[0]

// 构建选中的完整问题数据（包括用户编辑的字段）
const selectedIssues = recognizedIssues.value.filter((_, index) =>
  selectedIssueIds.value.has(index)
)

// 更新 noticeData 中的 issues 为选中的问题
const updatedNoticeData = {
  ...noticeData,
  issues: selectedIssues
}

const result = await importService.importSelected(updatedNoticeData, Array.from(selectedIssueIds.value))
```

**关键改进**：
- ✅ 提取选中的完整问题数据
- ✅ 包含用户编辑的 `issue_category`, `issue_type_level1`, `issue_type_level2`
- ✅ 将完整问题数据传递到后端

---

### 2. backend/app/main.py

**修改模型**：`ImportSelectedRequest`（第 17-21 行）

**修改前**：
```python
class ImportSelectedRequest(BaseModel):
    """导入选中记录的请求模型"""
    notice_data: Dict
    selected_issue_ids: List[str]
```

**修改后**：
```python
class ImportSelectedRequest(BaseModel):
    """导入选中记录的请求模型"""
    notice_data: Dict  # 包含完整的问题数据（包括用户编辑的字段）
    selected_issue_ids: List  # 选中的问题索引列表
```

**关键改进**：
- ✅ 更新注释说明 `notice_data` 包含完整问题数据
- ✅ 更新注释说明 `selected_issue_ids` 是索引列表

---

### 3. backend/app/services/import_service.py

**修改方法 1**：`_insert_issue` 问题类别处理（第 244-288 行）

**修改前**：
```python
# 使用分类器自动识别问题类别
issue_category = IssueCategoryClassifier.classify(
    description=issue['description'],
    site_name=issue.get('site_name'),
    section_name=issue.get('section_name')
)

# 如果分类器无法识别，默认设为施工安全
if not issue_category or issue_category == '其它':
    issue_category = '施工安全'
```

**修改后**：
```python
# 优先使用用户编辑的问题类别，只在为空时才使用自动分类
issue_category = issue.get('issue_category')

if not issue_category:
    # 使用分类器自动识别问题类别
    issue_category = IssueCategoryClassifier.classify(
        description=issue['description'],
        site_name=issue.get('site_name'),
        section_name=issue.get('section_name')
    )

    # 如果分类器无法识别，默认设为施工安全
    if not issue_category or issue_category == '其它':
        issue_category = '施工安全'

logger.info(f"[DEBUG] 问题类别来源: {'用户编辑' if issue.get('issue_category') else '自动分类'}")
logger.info(f"[DEBUG] issue_category: {issue_category}")
logger.info(f"[DEBUG] issue_type_level1: {issue.get('issue_type_level1')}")
logger.info(f"[DEBUG] issue_type_level2: {issue.get('issue_type_level2')}")
```

**关键改进**：
- ✅ 优先使用用户编辑的值
- ✅ 只在为空时才使用自动分类
- ✅ 添加日志记录来源和三层分类值

**修改方法 2**：INSERT 语句（第 307-339 行）

**修改前**：
```python
cursor.execute("""
    INSERT INTO issues
    (issue_number, supervision_notice_id, section_name, site_name, description,
     is_rectification_notice, is_bad_behavior_notice, document_section, document_source,
     severity, issue_category, inspection_unit, inspection_date, inspection_personnel,
     rectification_requirements, rectification_deadline, responsible_unit, responsible_person,
     created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    ...
    issue_category,  # 使用分类器识别的分类
    ...
))
```

**修改后**：
```python
cursor.execute("""
    INSERT INTO issues
    (issue_number, supervision_notice_id, section_name, site_name, description,
     is_rectification_notice, is_bad_behavior_notice, document_section, document_source,
     severity, issue_category, issue_type_level1, issue_type_level2, inspection_unit, inspection_date, inspection_personnel,
     rectification_requirements, rectification_deadline, responsible_unit, responsible_person,
     created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    ...
    issue_category,  # 使用用户编辑的分类或自动分类
    issue.get('issue_type_level1'),  # 用户编辑的二级分类
    issue.get('issue_type_level2'),  # 用户编辑的三级分类
    ...
))
```

**关键改进**：
- ✅ 添加 `issue_type_level1` 字段
- ✅ 添加 `issue_type_level2` 字段
- ✅ 从问题数据中获取这两个字段的值

---

## 🔄 数据流变更

### 修改前的数据流
```
用户编辑问题类别
    ↓
保存到 recognizedIssues
    ↓
点击导入
    ↓
只传递问题 ID 到后端 ❌
    ↓
后端重新分类（覆盖用户编辑的值）❌
    ↓
INSERT 语句没有三层分类字段 ❌
    ↓
数据库保存错误的值
```

### 修改后的数据流
```
用户编辑问题类别
    ↓
保存到 recognizedIssues
    ↓
点击导入
    ↓
传递完整问题数据到后端 ✅
    ↓
后端优先使用用户编辑的值 ✅
    ↓
INSERT 语句包含三层分类字段 ✅
    ↓
数据库保存正确的值
```

---

## 📊 影响范围

| 组件 | 影响 | 说明 |
|------|------|------|
| 前端编辑界面 | 无 | 编辑界面保持不变 |
| 前端状态管理 | 修改 | 传递完整问题数据 |
| 后端 API | 修改 | 接收完整问题数据 |
| 后端导入服务 | 修改 | 优先使用用户编辑值 |
| 数据库表结构 | 无 | 表结构保持不变 |
| 现有数据 | 无 | 不影响现有数据 |

---

**版本**：1.0
**最后更新**：2025-11-15

