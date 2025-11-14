# CDRLApp 导入功能改造 - 快速参考

## 🎯 一句话总结
将导入功能从"识别-直接导入"改造为"识别-缓存-确认-选择性导入"的多步骤流程。

---

## 📊 核心改变对比

### 当前流程
```
选择文件 → 识别 → 直接导入数据库 → 显示结果
```

### 目标流程
```
选择文件 → 识别 → 缓存到前端 → 用户预览编辑 → 用户选择 → 导入 → 显示结果
```

---

## 🔄 ViewMode 状态转移

```
upload → recognizing → preview-notices → preview-issues → confirm → importing → result
```

---

## 📝 新增状态（importStore.js）

```javascript
// 识别结果
recognizedNotices = []
recognizedIssues = []

// 用户选择
selectedNoticeIds = new Set()
selectedIssueIds = new Set()

// 编辑和验证
editedData = {}
validationErrors = {}
modifiedRecords = new Set()

// 流程状态
importStep = 1
importProgress = 0
```

---

## 🔌 新增 API

### 1. 修改现有 API
**POST /api/import/document**
- 改为只识别不导入
- 返回识别结果（通知书 + 问题列表）

### 2. 新增导入 API
**POST /api/notices/import-selected**
- 导入选中的通知书和问题
- 使用事务处理

---

## 🎨 新增组件

| 组件 | 功能 |
|------|------|
| `ImportPreviewNotices.vue` | 通知书列表预览 |
| `ImportPreviewIssues.vue` | 问题列表预览 |
| `ImportConfirm.vue` | 导入确认 |
| `ImportResult.vue` | 导入结果反馈 |

---

## 📂 文件修改清单

### 后端
- [ ] `backend/app/main.py` - 新增导入 API
- [ ] `backend/app/services/import_service.py` - 修改识别逻辑、新增导入方法

### 前端
- [ ] `frontend/src/stores/importStore.js` - 扩展状态和方法
- [ ] `frontend/src/pages/ImportPage.vue` - 集成新组件
- [ ] `frontend/src/components/ImportPreviewNotices.vue` - 新增
- [ ] `frontend/src/components/ImportPreviewIssues.vue` - 新增
- [ ] `frontend/src/components/ImportConfirm.vue` - 新增
- [ ] `frontend/src/components/ImportResult.vue` - 新增
- [ ] `frontend/src/services/importService.js` - 新增导入方法

---

## ⏱️ 工作量估算

| 任务 | 工作量 | 时间 |
|------|--------|------|
| 后端 API | 中 | 1-2 天 |
| 前端状态 | 中 | 1 天 |
| 前端组件 | 大 | 2-3 天 |
| 测试优化 | 中 | 1-2 天 |
| **总计** | **大** | **5-8 天** |

---

## 🚀 实施步骤

### 第 1 天
- [ ] 修改后端识别 API
- [ ] 新增后端导入 API

### 第 2 天
- [ ] 扩展 importStore.js
- [ ] 新增 importService 方法

### 第 3-4 天
- [ ] 创建预览组件
- [ ] 创建确认和结果组件

### 第 5 天
- [ ] 集成到 ImportPage.vue
- [ ] 修改步骤指示器

### 第 6-7 天
- [ ] 单元测试
- [ ] 集成测试

### 第 8 天
- [ ] 性能优化
- [ ] 用户体验优化

---

## 💾 关键代码片段

### 识别文档
```javascript
const recognizeDocument = async (file) => {
  const result = await importService.importDocument(file)
  recognizedNotices.value = [result.notice]
  recognizedIssues.value = result.issues
  viewMode.value = 'preview-notices'
}
```

### 导入选中
```javascript
const importSelected = async () => {
  const selectedIssues = recognizedIssues.value.filter(
    issue => selectedIssueIds.value.has(issue.id)
  )
  const result = await importService.importSelected({
    notice: recognizedNotices.value[0],
    issues: selectedIssues
  })
  return result
}
```

### 编辑记录
```javascript
const editRecord = (recordId, fieldName, value) => {
  if (!editedData.value[recordId]) {
    editedData.value[recordId] = {}
  }
  editedData.value[recordId][fieldName] = value
  modifiedRecords.value.add(recordId)
  validateRecord(recordId)
}
```

---

## ✅ 验收清单

### 功能
- [ ] 用户可以预览识别结果
- [ ] 用户可以编辑识别结果
- [ ] 用户可以选择性导入
- [ ] 导入成功后显示结果反馈
- [ ] 支持批量导入

### 质量
- [ ] 数据验证正常工作
- [ ] 错误处理完善
- [ ] 性能满足要求
- [ ] 代码覆盖率 > 80%

### 兼容性
- [ ] 不破坏现有功能
- [ ] 支持主流浏览器
- [ ] 向后兼容

---

## 🔗 相关文档

| 文档 | 说明 |
|------|------|
| `IMPORT_WORKFLOW_REDESIGN_PLAN.md` | 改造方案 |
| `IMPORT_WORKFLOW_DETAILED_DESIGN.md` | 详细设计 |
| `IMPORT_COMPONENTS_DESIGN.md` | 组件设计 |
| `IMPORT_IMPLEMENTATION_GUIDE.md` | 实施指南 |
| `IMPORT_REDESIGN_EXECUTIVE_SUMMARY.md` | 执行总结 |

---

## 🎓 技术栈

### 前端
- Vue 3 Composition API
- Pinia 状态管理
- Element Plus UI 组件库
- Axios HTTP 客户端

### 后端
- FastAPI 框架
- SQLite 数据库
- Python 3.8+

---

## 📞 常见问题

### Q: 为什么要改造导入功能？
A: 提高数据质量，给用户充分的时间预览和编辑数据。

### Q: 改造会破坏现有功能吗？
A: 不会。我们保持现有的状态和方法，新流程使用新的状态和方法。

### Q: 需要多长时间完成？
A: 预计 5-8 天，取决于团队规模和经验。

### Q: 如何处理大量数据？
A: 使用虚拟滚动（>100 条）和分页（>500 条）。

### Q: 如何处理导入失败？
A: 显示错误详情，支持修改后重试。

---

## 🎯 成功指标

| 指标 | 目标 | 预期 |
|------|------|------|
| 数据质量 | 提高 30-50% | ✅ |
| 用户体验 | 改善 40-60% | ✅ |
| 数据错误 | 减少 50-70% | ✅ |
| 用户满意度 | 提高 60-80% | ✅ |

---

## 📅 时间表

```
第 1 周: 后端 API 改造 + 前端状态管理
第 2 周: 前端 UI 组件开发
第 3 周: 测试和优化
第 4 周: 发布上线
```

---

**版本**: v1.0
**更新**: 2025-11-14
**状态**: 待审批

