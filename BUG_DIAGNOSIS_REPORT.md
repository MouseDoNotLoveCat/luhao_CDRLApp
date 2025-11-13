# CDRLApp 导入功能 BUG 诊断报告

## BUG 1: 导入成功后显示的通知书列表不正确

### 问题描述
- **预期**: 导入成功后，应该只显示本次导入的通知书列表
- **实际**: 显示的是数据库中已导入的所有通知书列表

### 根本原因分析

**ImportPage.vue 第 300-304 行**:
```javascript
setTimeout(async () => {
  // 刷新通知书列表
  await noticeStore.fetchNotices()  // ❌ 获取所有通知书
  importStore.goToNoticesList()
}, 500)
```

**问题**: 调用了 `noticeStore.fetchNotices()` 获取所有通知书，而不是显示 `importStore.importedNotices`（本次导入的通知书）

### 解决方案

**应该**:
1. 不调用 `noticeStore.fetchNotices()`
2. 直接调用 `importStore.goToNoticesList()`
3. 让 NoticesListComponent 显示 `importStore.importedNotices` 而不是 `noticeStore.notices`

---

## BUG 2: 界面状态混淆问题

### 问题描述
1. 导入成功后，点击通知书列表中的"详情"按钮无效
2. 再次点击"导入监督检查通知书"菜单时，界面下方出现之前点击的通知书详情界面

### 根本原因分析

**问题 1: 详情按钮无效**
- NoticesListComponent 中的 `handleViewDetail` 方法调用 `store.selectNotice(row)`
- 但 `store` 是 `noticeManagementStore`，不是 `importStore`
- 而 ImportPage 中的 viewMode 是由 `importStore` 控制的
- 所以点击详情按钮无法改变 `importStore.viewMode`

**问题 2: 返回导入界面时出现详情界面**
- `importStore.goBackToUpload()` 重置了 `viewMode = 'upload'`
- 但 `noticeManagementStore` 中的状态未被重置
- 导致界面叠加显示

### 解决方案

1. **修改 NoticesListComponent**:
   - 改为使用 `importStore` 而不是 `noticeManagementStore`
   - 或者添加事件发射，让 ImportPage 处理详情按钮点击

2. **修改 ImportPage**:
   - 在 `goBackToUpload()` 时，同时重置 `noticeManagementStore` 的状态

3. **修改 importStore.goBackToUpload()**:
   - 添加重置 `noticeManagementStore` 状态的逻辑

---

## 修复策略

### 修复 BUG 1
- 移除 `await noticeStore.fetchNotices()` 调用
- 让 NoticesListComponent 显示 `importStore.importedNotices`

### 修复 BUG 2
- 修改 NoticesListComponent 使用 `importStore`
- 或者在 ImportPage 中处理详情按钮点击事件
- 确保 `goBackToUpload()` 完全重置所有状态

---

## 相关代码位置

| 文件 | 行号 | 问题 |
|------|------|------|
| ImportPage.vue | 300-304 | 调用了 noticeStore.fetchNotices() |
| NoticesListComponent.vue | 87, 98 | 使用了 noticeManagementStore |
| importStore.js | 305-311 | goBackToUpload() 未重置 noticeManagementStore |

