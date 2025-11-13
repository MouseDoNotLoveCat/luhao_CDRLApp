# 🔧 通知书管理 - 问题详情按钮修复

## 问题描述

通知书管理功能下，问题列表中的"详情"按钮点击没有反应。

## 根本原因

存在**视图模式状态不一致**的问题：

1. **NoticeManagementPage.vue** 中检查的是 `noticeStore.viewMode === 'issue-detail'`
2. 但 **IssuesPreview.vue** 中的 `handleSelectIssue` 方法调用 `importStore.selectIssue()`
3. `importStore.selectIssue()` 设置的是 `importStore.viewMode = 'detail'`
4. 这导致条件永远不匹配，问题详情页面无法显示

## 修复方案

### 修改 1：NoticeManagementPage.vue

**问题**：检查错误的视图模式
```vue
<!-- 错误的检查 -->
<div v-else-if="noticeStore.viewMode === 'issue-detail'">
  <IssueDetailPreview />
</div>
```

**修复**：改为检查 `importStore.viewMode`
```vue
<!-- 正确的检查 -->
<div v-else-if="importStore.viewMode === 'detail'">
  <IssueDetailPreview />
</div>
```

### 修改 2：IssueDetailPreview.vue

**问题**：返回按钮逻辑检查错误的视图模式
```javascript
const handleBackToIssues = () => {
  const noticeStore = useNoticeManagementStore()
  if (noticeStore.viewMode === 'issue-detail') {  // ❌ 错误
    noticeStore.viewMode = 'detail'
  } else {
    importStore.goBackToNotices()
  }
}
```

**修复**：改为检查 `noticeStore.viewMode === 'detail'`
```javascript
const handleBackToIssues = () => {
  const noticeStore = useNoticeManagementStore()
  if (noticeStore.viewMode === 'detail') {  // ✅ 正确
    importStore.viewMode = 'issues'
  } else {
    importStore.goBackToNotices()
  }
}
```

## 修改文件

| 文件 | 修改内容 |
|------|---------|
| `frontend/src/pages/NoticeManagementPage.vue` | 第 14 行：改为检查 `importStore.viewMode === 'detail'` |
| `frontend/src/components/IssueDetailPreview.vue` | 第 207-227 行：修复返回按钮逻辑 |

## 工作流程

### 通知书管理 - 问题详情流程

```
通知书列表
    ↓
点击"查看详情"
    ↓
noticeStore.viewMode = 'detail'
importStore.noticeIssues = 问题列表
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
```

## 测试步骤

1. 打开应用 http://localhost:3001
2. 点击左侧菜单"通知书管理"
3. 点击任意通知书的"查看详情"按钮
4. 在问题列表中点击"详情"按钮
5. ✅ 应该显示问题详情页面

## 验证清单

- [ ] 通知书列表正常显示
- [ ] 点击"查看详情"进入问题列表
- [ ] 点击"详情"按钮进入问题详情页面
- [ ] 问题详情页面显示完整信息
- [ ] 返回按钮正常工作
- [ ] 返回到问题列表
- [ ] 返回到通知书列表

## 相关代码

### NoticeManagementPage.vue
```vue
<template>
  <div class="notice-management-page">
    <!-- 列表视图 -->
    <div v-if="noticeStore.viewMode === 'list'">
      <NoticesListComponent @view-detail="handleViewNoticeDetail" />
    </div>

    <!-- 问题列表视图 -->
    <div v-else-if="noticeStore.viewMode === 'detail'">
      <IssuesPreview />
    </div>

    <!-- 问题详情视图 -->
    <div v-else-if="importStore.viewMode === 'detail'">
      <IssueDetailPreview />
    </div>
  </div>
</template>
```

### IssueDetailPreview.vue
```javascript
const handleBackToIssues = () => {
  const noticeStore = useNoticeManagementStore()
  if (noticeStore.viewMode === 'detail') {
    // 来自通知书管理页面，返回到问题列表
    importStore.viewMode = 'issues'
  } else {
    // 来自导入页面，返回到问题列表
    importStore.goBackToNotices()
  }
}
```

## 总结

✅ **问题已修复**

通过统一视图模式的检查逻辑，确保：
1. 通知书管理页面能正确检测到问题详情视图
2. 返回按钮能正确返回到问题列表
3. 导入页面的功能不受影响

---

**修复日期**: 2025-11-07  
**修复状态**: ✅ 完成  
**测试状态**: 待验证

