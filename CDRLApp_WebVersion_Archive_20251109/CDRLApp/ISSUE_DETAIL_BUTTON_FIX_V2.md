# 🔧 通知书管理 - 问题详情按钮修复 V2

## 问题描述

通知书管理功能下，问题列表中的"详情"按钮点击没有反应。

## 根本原因分析

经过深入调查，发现有**两个层面的问题**：

### 问题 1：视图模式状态不一致（已修复）
- NoticeManagementPage.vue 检查的是 `noticeStore.viewMode === 'issue-detail'`
- 但实际设置的是 `importStore.viewMode = 'detail'`
- 导致条件不匹配

### 问题 2：后端 API 返回数据不完整（已修复）
- `/api/notices/{notice_id}` 端点返回的问题对象缺少必要字段
- 前端 IssueDetailPreview.vue 期望的字段与后端返回的字段不匹配

## 修复方案

### 修复 1：NoticeManagementPage.vue

改为检查 `importStore.viewMode`：
```vue
<div v-else-if="importStore.viewMode === 'detail'">
  <IssueDetailPreview />
</div>
```

### 修复 2：IssueDetailPreview.vue

修复返回按钮逻辑：
```javascript
const handleBackToIssues = () => {
  const noticeStore = useNoticeManagementStore()
  if (noticeStore.viewMode === 'detail') {
    importStore.viewMode = 'issues'
  } else {
    importStore.goBackToNotices()
  }
}
```

### 修复 3：backend/app/main.py - `/api/notices/{notice_id}` 端点

**原问题**：
- 返回的问题对象字段名不匹配
- 缺少 `project_name`、`section_name` 等字段
- 字段名 `issue_type` 应该是 `issue_type_level1`

**修复方案**：
```python
# 获取关联的问题列表（包含项目和标段信息）
cursor.execute("""
    SELECT i.id, i.site_name, i.description, i.issue_type_level1, i.issue_type_level2,
           i.severity, i.rectification_deadline, i.is_rectification_notice, 
           i.document_section, i.created_at, sn.check_date, sn.check_unit,
           s.section_name, p.project_name
    FROM issues i
    LEFT JOIN supervision_notices sn ON i.supervision_notice_id = sn.id
    LEFT JOIN sections s ON i.section_id = s.id
    LEFT JOIN projects p ON s.project_id = p.id
    WHERE i.supervision_notice_id = ?
    ORDER BY i.created_at DESC
""", (notice_id,))
```

**返回格式**：
```python
'issues': [
    {
        'id': row[0],
        'site_name': row[1],
        'description': row[2],
        'issue_type_level1': row[3],
        'issue_type_level2': row[4],
        'severity': row[5],
        'rectification_deadline': row[6],
        'is_rectification': row[7],
        'document_section': row[8],
        'created_at': row[9],
        'check_date': row[10],
        'check_unit': row[11],
        'section_name': row[12],
        'project_name': row[13]
    }
    for row in issues_rows
]
```

## 修改文件

| 文件 | 修改内容 |
|------|---------|
| `frontend/src/pages/NoticeManagementPage.vue` | 第 14 行：改为检查 `importStore.viewMode === 'detail'` |
| `frontend/src/components/IssueDetailPreview.vue` | 第 207-227 行：修复返回按钮逻辑 |
| `backend/app/main.py` | 第 362-405 行：修复 `/api/notices/{notice_id}` 端点，添加 JOIN 查询和完整字段 |

## 返回的问题对象字段对应关系

| 前端期望字段 | 后端返回字段 | 数据来源 |
|-------------|-----------|--------|
| `id` | `i.id` | issues 表 |
| `site_name` | `i.site_name` | issues 表 |
| `description` | `i.description` | issues 表 |
| `issue_type_level1` | `i.issue_type_level1` | issues 表 |
| `issue_type_level2` | `i.issue_type_level2` | issues 表 |
| `severity` | `i.severity` | issues 表 |
| `rectification_deadline` | `i.rectification_deadline` | issues 表 |
| `is_rectification` | `i.is_rectification_notice` | issues 表 |
| `document_section` | `i.document_section` | issues 表 |
| `check_date` | `sn.check_date` | supervision_notices 表 |
| `check_unit` | `sn.check_unit` | supervision_notices 表 |
| `section_name` | `s.section_name` | sections 表 |
| `project_name` | `p.project_name` | projects 表 |

## 工作流程

```
通知书列表
    ↓
点击"查看详情"
    ↓
noticeStore.viewMode = 'detail'
importStore.noticeIssues = 问题列表（包含完整字段）
    ↓
显示 IssuesPreview 组件
    ↓
点击"详情"按钮
    ↓
handleSelectIssue(issue)
    ↓
importStore.selectIssue(issue.id)
    ↓
importStore.viewMode = 'detail'  ✅
    ↓
NoticeManagementPage 检查 importStore.viewMode === 'detail'  ✅
    ↓
显示 IssueDetailPreview 组件  ✅
    ↓
currentIssue = importStore.noticeIssues.find(issue => issue.id === importStore.selectedIssueId)  ✅
    ↓
显示问题详情页面  ✅
```

## 测试步骤

1. 打开应用 http://localhost:3001
2. 点击左侧菜单"通知书管理"
3. 点击任意通知书的"查看详情"按钮
4. 在问题列表中点击"详情"按钮
5. ✅ 应该显示问题详情页面，包含所有字段

## 验证清单

- [ ] 通知书列表正常显示
- [ ] 点击"查看详情"进入问题列表
- [ ] 问题列表显示完整信息
- [ ] 点击"详情"按钮进入问题详情页面
- [ ] 问题详情页面显示完整信息（包括项目名称、标段名称等）
- [ ] 返回按钮正常工作
- [ ] 返回到问题列表
- [ ] 返回到通知书列表

## 相关 API 端点

### GET /api/notices/{notice_id}
获取通知书详情及其关联的问题列表

**请求**：
```
GET /api/notices/1
```

**响应**：
```json
{
  "id": 1,
  "notice_number": "2025-001",
  "check_date": "2025-01-01",
  "check_unit": "质量监督站",
  "check_personnel": "张三",
  "inspection_basis": "铁路工程质量验收标准",
  "created_at": "2025-01-01T00:00:00",
  "issues": [
    {
      "id": 1,
      "site_name": "藤县北站",
      "description": "混凝土强度不足",
      "issue_type_level1": "质量问题",
      "issue_type_level2": "混凝土质量",
      "severity": 3,
      "rectification_deadline": "2025-02-01",
      "is_rectification": false,
      "document_section": "第3章",
      "created_at": "2025-01-01T00:00:00",
      "check_date": "2025-01-01",
      "check_unit": "质量监督站",
      "section_name": "第一标段",
      "project_name": "黄百铁路"
    }
  ]
}
```

---

**修复日期**: 2025-11-07  
**修复状态**: ✅ 完成  
**测试状态**: 待验证

