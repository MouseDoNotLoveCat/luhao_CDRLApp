# 通知书管理 - 问题详情按钮调试指南

## 🔍 调试步骤已完成

我已经添加了详细的调试代码到前端，以帮助诊断问题详情按钮不响应的问题。

### ✅ 已验证的内容

1. **后端 API 正常工作** ✅
   - 测试 API 端点：`GET /api/notices/1`
   - 返回完整的问题对象，包含所有必要字段：
     - `id` ✅
     - `site_name` ✅
     - `description` ✅
     - `issue_type_level1` ✅
     - `issue_type_level2` ✅
     - `severity` ✅
     - `check_date` ✅
     - `check_unit` ✅
     - `section_name` ✅
     - `project_name` ✅

2. **前端服务正常运行** ✅
   - 后端：http://localhost:8000 ✅
   - 前端：http://localhost:3000 ✅

### 🔧 添加的调试代码

#### 1. NoticeManagementPage.vue
- 添加 `watch` 监听 `importStore.viewMode` 变化
- 添加 `watch` 监听 `noticeStore.viewMode` 变化
- 在 `handleViewNoticeDetail` 中添加 console.log

#### 2. IssuesPreview.vue
- 在 `handleSelectIssue` 中添加详细的 console.log
- 记录 issue 对象和 ID

#### 3. IssueDetailPreview.vue
- 在 `currentIssue` computed 属性中添加详细的 console.log
- 记录 `noticeIssues` 数组和 `selectedIssueId`

#### 4. importStore.js
- 在 `selectIssue` 方法中添加详细的 console.log
- 记录 `noticeIssues` 数组内容

#### 5. noticeManagementStore.js
- 在 `fetchNoticeDetail` 中添加同步到 importStore 的代码
- 添加详细的 console.log 记录同步过程

## 📋 测试步骤

请按照以下步骤进行测试，并在浏览器开发者工具中查看 Console 输出：

### 步骤 1：打开浏览器开发者工具
```
按 F12 打开开发者工具
选择 Console 标签页
```

### 步骤 2：导航到通知书管理
1. 打开应用 http://localhost:3000
2. 点击左侧菜单"通知书管理"
3. 在 Console 中查看是否有错误信息

### 步骤 3：点击"查看详情"
1. 点击任意通知书的"查看详情"按钮
2. 在 Console 中查看以下日志：
   ```
   🔍 handleViewNoticeDetail called with notice: {...}
   🔍 Syncing to importStore...
   🔍 noticeStore.viewMode changed to: detail
   ```

### 步骤 4：点击问题列表中的"详情"按钮
1. 在问题列表中点击任意问题的"详情"按钮
2. 在 Console 中查看以下日志：
   ```
   🔍 handleSelectIssue called with issue: {...}
   🔍 selectIssue called with issueId: ...
   🔍 importStore.viewMode changed to: detail
   🔍 Computing currentIssue...
   Found issue: {...}
   ```

## 🐛 可能的问题

### 问题 1：noticeIssues 数组为空
**症状**：`importStore.noticeIssues` 为空数组
**原因**：数据同步失败
**解决方案**：检查 `fetchNoticeDetail` 是否正确返回问题列表

### 问题 2：selectedIssueId 不匹配
**症状**：`currentIssue` 为 undefined
**原因**：问题 ID 不在 `noticeIssues` 数组中
**解决方案**：检查问题对象的 `id` 字段是否正确

### 问题 3：viewMode 未正确切换
**症状**：页面不显示问题详情
**原因**：`importStore.viewMode` 未设置为 'detail'
**解决方案**：检查 `selectIssue` 方法是否被调用

## 📝 Console 输出示例

### 正常流程的 Console 输出：
```
🔍 handleViewNoticeDetail called with notice: {id: 1, notice_number: "南宁站[2025]（通知）黄百10号", ...}
🔍 Syncing to importStore...
   noticeIssues: Array(65) [...]
   After sync, importStore.noticeIssues: Array(65) [...]
🔍 noticeStore.viewMode changed to: detail
🔍 handleSelectIssue called with issue: {id: 1200, site_name: "李家村隧道出口", ...}
   issue.id: 1200
🔍 selectIssue called with issueId: 1200
   Current noticeIssues: Array(65) [...]
   After selectIssue, viewMode: detail
   selectedIssueId: 1200
🔍 importStore.viewMode changed to: detail
🔍 Computing currentIssue...
   importStore.noticeIssues: Array(65) [...]
   importStore.selectedIssueId: 1200
   Found issue: {id: 1200, site_name: "李家村隧道出口", ...}
```

## 🚀 下一步

1. 打开浏览器开发者工具（F12）
2. 导航到通知书管理
3. 点击"查看详情"
4. 点击问题列表中的"详情"按钮
5. 在 Console 中查看日志输出
6. 将 Console 输出告诉我，以便进一步诊断问题

---

**调试日期**: 2025-11-07  
**调试状态**: 🔍 进行中  
**需要用户反馈**: ✅ 是

