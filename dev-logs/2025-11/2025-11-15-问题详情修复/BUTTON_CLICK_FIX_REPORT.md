# 🔧 导入预览组件按钮点击事件修复报告

## 问题诊断

在测试导入功能时，发现两个按钮无法正常工作，浏览器 Console 中出现错误：

### 错误 1：查看问题按钮
```
Uncaught TypeError: Cannot create property 'value' on number '0'
at Proxy.handleViewIssues (ImportPreviewNotices.vue:64:47)
```

**原因**：在 `handleViewIssues` 方法中，错误地尝试给 `currentRecognizedNoticeId.value` 赋值
```javascript
// ❌ 错误的方式
importStore.currentRecognizedNoticeId.value = index
```

### 错误 2：移除按钮
```
Uncaught TypeError: Cannot read properties of undefined (reading 'splice')
at Proxy.handleRemove (ImportPreviewNotices.vue:69:39)
```

**原因**：在 `handleRemove` 方法中，错误地访问 `recognizedNotices.value`
```javascript
// ❌ 错误的方式
importStore.recognizedNotices.value.splice(index, 1)
```

### 错误 3：下一步按钮（ImportPreviewIssues）
```
// ❌ 错误的方式
importStore.viewMode.value = 'confirm'
```

**原因**：与其他 viewMode 赋值方式不一致

## 修复方案

### 修复 1：handleViewIssues
```javascript
// ✅ 正确的方式
const handleViewIssues = (index) => {
  importStore.currentRecognizedNoticeId = index
  importStore.previewIssues()
}
```

**说明**：
- `currentRecognizedNoticeId` 是 `ref(null)`
- 在 script 中应该直接赋值，不需要 `.value`
- Pinia 会自动处理 ref 的解包

### 修复 2：handleRemove
```javascript
// ✅ 正确的方式
const handleRemove = (index) => {
  recognizedNotices.value.splice(index, 1)
  if (recognizedNotices.value.length === 0) {
    importStore.goBackToUpload()
  }
}
```

**说明**：
- `recognizedNotices` 是一个 computed 属性，返回 `importStore.recognizedNotices`
- 应该直接使用 `recognizedNotices.value`，而不是 `importStore.recognizedNotices.value`

### 修复 3：handleConfirm
```javascript
// ✅ 正确的方式
const handleConfirm = () => {
  if (selectedIssueIds.value.size === 0) {
    ElMessage.warning('请先选择至少一个问题')
    return
  }
  importStore.viewMode = 'confirm'
}
```

**说明**：
- 与其他 viewMode 赋值方式保持一致
- 直接赋值，不需要 `.value`

## 修改文件

| 文件 | 修改内容 |
|------|---------|
| `frontend/src/components/ImportPreviewNotices.vue` | 修复 handleViewIssues 和 handleRemove |
| `frontend/src/components/ImportPreviewIssues.vue` | 修复 handleConfirm 中的 viewMode 赋值 |

## 测试步骤

1. **启动应用**：`./start-dev.sh`
2. **打开浏览器**：http://localhost:3000
3. **测试查看问题按钮**：
   - 点击"导入文件"
   - 在通知书列表中点击"查看问题"
   - 验证能否正确跳转到问题预览界面
4. **测试移除按钮**：
   - 点击"导入文件"
   - 在通知书列表中点击"移除"
   - 验证通知书是否被移除
5. **测试下一步按钮**：
   - 在问题预览界面选择问题
   - 点击"下一步"
   - 验证能否正确跳转到确认导入界面

## 预期结果

✅ 查看问题按钮能正常工作，跳转到问题预览界面
✅ 移除按钮能正常工作，从列表中移除通知书
✅ 下一步按钮能正常工作，跳转到确认导入界面
✅ 浏览器 Console 中没有错误信息

## Git 提交

```
0c8c16e - fix: Fix button click handlers in ImportPreviewNotices and ImportPreviewIssues
```

## 关键学习点

1. **Pinia ref 赋值**：在 script 中直接赋值 ref，不需要 `.value`
2. **Computed 属性**：使用 computed 属性时，需要使用 `.value` 访问其值
3. **代码一致性**：确保相同类型的操作使用相同的方式

---

**修复状态**：✅ 已完成
**测试状态**：⏳ 待测试

