# 导入界面无法返回问题 - 诊断报告

## 问题描述

**症状**: 
1. 第一次导入：点击"导入监督检查通知书"按钮 → 导入成功 → 自动跳转到"通知书一览表"（正常）
2. 第二次导入：再次点击"导入监督检查通知书"按钮 → 始终停留在"通知书一览表"（异常）

**预期**: 应该返回导入界面

## 根本原因分析

### 问题流程

```
第一次导入:
  1. 点击"导入监督检查通知书"菜单 → activeMenu = 'import'
  2. ImportPage 显示，importStore.viewMode = 'upload'（初始值）
  3. 导入成功 → importStore.viewMode = 'notices'
  4. 显示 NoticesListComponent

第二次导入:
  1. 点击"导入监督检查通知书"菜单 → activeMenu = 'import'
  2. ImportPage 显示，但 importStore.viewMode 仍然是 'notices'（未重置！）
  3. 显示 NoticesListComponent（而不是导入界面）
  ❌ 问题：viewMode 没有被重置
```

### 代码分析

**App.vue 中的菜单点击处理**:
```javascript
@click="activeMenu = 'import'"
```

这只改变了 `activeMenu`，但没有重置 `importStore.viewMode`。

**ImportPage.vue 中的视图切换**:
```vue
<div v-if="importStore.viewMode === 'upload'" class="import-container">
  <!-- 导入界面 -->
</div>
<div v-else-if="importStore.viewMode === 'notices'">
  <NoticesListComponent />
</div>
```

当 `viewMode` 是 `'notices'` 时，显示通知书列表，而不是导入界面。

### 为什么会这样

1. **导入成功后**: `importStore.goToNoticesList()` 将 `viewMode` 设置为 `'notices'`
2. **再次点击菜单**: `activeMenu` 改变为 `'import'`，但 `importStore.viewMode` 仍然是 `'notices'`
3. **结果**: ImportPage 显示通知书列表，而不是导入界面

## 解决方案

需要在 App.vue 中添加逻辑：当点击"导入监督检查通知书"菜单时，重置 `importStore.viewMode` 为 `'upload'`。

### 修改步骤

1. 在 App.vue 中导入 `useImportStore`
2. 在菜单点击处理中调用 `importStore.goBackToUpload()`

```javascript
// App.vue
import { useImportStore } from './stores/importStore'

const importStore = useImportStore()

// 修改菜单点击处理
const handleImportMenuClick = () => {
  activeMenu.value = 'import'
  importStore.goBackToUpload()  // 重置 viewMode 为 'upload'
}
```

## 相关代码

### importStore.js 中已有的方法
```javascript
const goBackToUpload = () => {
  viewMode.value = 'upload'
  selectedNoticeId.value = null
  selectedIssueId.value = null
  importedNotices.value = []
  noticeIssues.value = []
}
```

这个方法已经存在，只需要在 App.vue 中调用它。

## 修复方案总结

✅ **问题**: importStore.viewMode 在导入成功后被设置为 'notices'，再次点击菜单时未被重置
✅ **解决**: 在 App.vue 中添加菜单点击处理，调用 `importStore.goBackToUpload()`
✅ **影响**: 最小化，只需修改 App.vue
✅ **测试**: 验证能否在导入界面和通知书一览表之间正常切换

