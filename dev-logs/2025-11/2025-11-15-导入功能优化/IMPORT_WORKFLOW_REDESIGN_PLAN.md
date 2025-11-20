# CDRLApp 导入功能流程改造方案

## 📋 执行摘要

将导入功能从"识别-直接导入"改造为"识别-缓存-确认-选择性导入"的多步骤流程。

### 核心改变
- **当前**: 用户选择文件 → 系统识别 → 直接导入数据库 → 显示结果
- **目标**: 用户选择文件 → 系统识别 → 缓存到前端 → 用户确认编辑 → 选择性导入 → 显示结果

### 预期收益
✅ 用户可以在导入前预览和编辑数据
✅ 用户可以选择性导入（不是全部导入）
✅ 提高数据质量和用户体验
✅ 支持批量操作和数据验证

---

## 🏗️ 架构设计

### 1. 前端状态管理扩展

**importStore.js 新增状态**:
```javascript
// 识别结果缓存（未导入）
const recognizedNotices = ref([])  // 识别的通知书列表
const recognizedIssues = ref([])   // 识别的问题列表

// 用户选择状态
const selectedNoticeIds = ref([])  // 选中的通知书 ID 数组
const selectedIssueIds = ref([])   // 选中的问题 ID 数组

// 编辑和验证状态
const editedData = ref({})         // 用户编辑的数据
const validationErrors = ref({})   // 数据验证错误
const modifiedRecords = ref(new Set())  // 已修改的记录 ID

// 导入流程状态
const importStep = ref(1)          // 当前步骤 (1-5)
const importProgress = ref(0)      // 导入进度 (0-100)
```

### 2. ViewMode 状态机扩展

**ImportPage.vue 的 viewMode 值**:
- `'upload'` - 文件选择界面
- `'recognizing'` - 识别中（显示加载状态）
- `'preview-notices'` - **新增**：识别结果预览（通知书列表）
- `'preview-issues'` - **新增**：识别结果预览（问题列表）
- `'confirm'` - **新增**：导入确认界面
- `'importing'` - **新增**：导入中（显示进度）
- `'result'` - **新增**：导入结果反馈
- `'notices'` - 已导入的通知书列表（保持原有）

### 3. 数据流程

```
用户选择文件
    ↓
调用识别 API (POST /api/import/document)
    ↓
后端返回识别结果（不导入数据库）
    ↓
前端缓存到 recognizedNotices/recognizedIssues
    ↓
显示预览界面（通知书列表）
    ↓
用户编辑、选择记录
    ↓
显示确认界面
    ↓
用户点击"确认导入"
    ↓
调用导入 API (POST /api/notices/import-selected)
    ↓
后端导入选中的记录
    ↓
显示导入结果反馈
```

---

## 📝 API 设计

### 后端 API 修改

#### 1. 修改现有 API（识别不导入）

**POST /api/import/document** (修改)
- **功能**: 识别 Word 文档，返回识别结果（不导入数据库）
- **参数**: `file` (FormData)
- **返回**:
```json
{
  "success": true,
  "notice": {
    "id": "temp_123",
    "notice_number": "南宁站[2025]（通知）黄百10号",
    "check_date": "2025-08-20",
    "check_unit": "南宁监督站",
    "check_personnel": "李规录、陈胜",
    "project_name": "黄百铁路",
    "issues_count": 65
  },
  "issues": [
    {
      "id": "temp_issue_1",
      "site_name": "工点 1",
      "description": "问题描述",
      "is_rectification_notice": true,
      ...20 个字段
    }
  ]
}
```

#### 2. 新增导入 API

**POST /api/notices/import-selected** (新增)
- **功能**: 导入选中的通知书和问题
- **参数**:
```json
{
  "notice": { ...通知书数据 },
  "issues": [ ...问题数据数组 ]
}
```
- **返回**:
```json
{
  "success": true,
  "notice_id": 123,
  "imported_issues_count": 65,
  "errors": []
}
```

---

## 🎨 UI/UX 设计

### 步骤指示器
```
步骤 1: 选择文件 ✓
步骤 2: 识别中... ⏳
步骤 3: 确认识别结果 ← 当前
步骤 4: 导入中...
步骤 5: 导入完成
```

### 预览界面（通知书列表）
- 表格显示：通知书编号、检查日期、检查单位、问题数量
- 每行提供复选框
- 全选/全不选功能
- "查看问题"按钮

### 预览界面（问题列表）
- 表格显示：20 列问题字段
- 每行提供复选框
- 行内编辑功能
- 返回通知书列表按钮

### 确认界面
- 显示选中的通知书数量和问题数量
- 显示数据验证状态
- "确认导入"和"取消"按钮

---

## 📂 文件修改计划

### 前端文件

| 文件 | 修改类型 | 优先级 | 工作量 |
|------|---------|--------|--------|
| `frontend/src/stores/importStore.js` | 修改 | P0 | 中 |
| `frontend/src/pages/ImportPage.vue` | 修改 | P0 | 大 |
| `frontend/src/components/ImportPreviewNotices.vue` | 新增 | P0 | 中 |
| `frontend/src/components/ImportPreviewIssues.vue` | 新增 | P0 | 中 |
| `frontend/src/components/ImportConfirm.vue` | 新增 | P0 | 小 |
| `frontend/src/components/ImportResult.vue` | 新增 | P0 | 小 |
| `frontend/src/services/importService.js` | 修改 | P0 | 小 |

### 后端文件

| 文件 | 修改类型 | 优先级 | 工作量 |
|------|---------|--------|--------|
| `backend/app/main.py` | 修改 | P0 | 小 |
| `backend/app/services/import_service.py` | 修改 | P0 | 中 |

---

## 🔄 实施步骤

### 第 1 阶段：后端 API 改造（1-2 天）
1. 修改 `/api/import/document` 为识别不导入
2. 新增 `/api/notices/import-selected` API
3. 添加事务处理和错误处理

### 第 2 阶段：前端状态管理（1 天）
1. 扩展 importStore.js 状态
2. 添加新的 action 方法
3. 添加数据验证逻辑

### 第 3 阶段：前端 UI 组件（2-3 天）
1. 创建预览组件（通知书、问题）
2. 创建确认组件
3. 创建结果反馈组件
4. 修改 ImportPage.vue 集成新流程

### 第 4 阶段：测试和优化（1-2 天）
1. 单元测试
2. 集成测试
3. 性能优化
4. 用户体验优化

---

## ⚠️ 注意事项

### 向后兼容性
- 保持现有的 `importedNotices` 和 `noticeIssues` 状态
- 保持现有的导航方法（`goToNoticesList` 等）
- 不破坏现有的通知书管理功能

### 性能考虑
- 大量数据（>100 条）使用虚拟滚动
- 编辑操作实时保存到前端状态
- 导入时显示进度条

### 数据验证
- 前端验证：必填字段、格式、长度
- 后端验证：业务规则、重复检测、数据一致性
- 验证失败时禁用导入按钮

---

## 📊 预估工作量

| 阶段 | 工作量 | 时间 |
|------|--------|------|
| 后端 API 改造 | 中 | 1-2 天 |
| 前端状态管理 | 中 | 1 天 |
| 前端 UI 组件 | 大 | 2-3 天 |
| 测试和优化 | 中 | 1-2 天 |
| **总计** | **大** | **5-8 天** |

---

## ✅ 验收标准

- [ ] 用户可以预览识别结果
- [ ] 用户可以编辑识别结果
- [ ] 用户可以选择性导入
- [ ] 导入成功后显示结果反馈
- [ ] 支持批量导入
- [ ] 数据验证正常工作
- [ ] 性能满足要求（<100ms 响应时间）
- [ ] 不破坏现有功能

---

## 🚀 后续优化方向

1. **冲突检测**: 检测通知书编号是否与数据库中已有记录重复
2. **异步处理**: 大量数据导入时使用后台任务
3. **导入历史**: 记录导入历史和操作日志
4. **数据对比**: 显示新导入数据与已有数据的差异
5. **模板导出**: 支持导出识别结果为 Excel 进行离线编辑

