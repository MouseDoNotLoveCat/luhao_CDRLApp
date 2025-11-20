# CDRLApp 导入功能详细设计文档

## 1. 状态机设计

### ViewMode 状态转移图

```
upload (初始状态)
  ↓ (用户选择文件并点击导入)
recognizing (识别中)
  ↓ (识别完成)
preview-notices (预览通知书列表)
  ↓ (用户点击"查看问题")
preview-issues (预览问题列表)
  ↓ (用户点击"返回" 或 "确认导入")
confirm (导入确认)
  ↓ (用户点击"确认导入")
importing (导入中)
  ↓ (导入完成)
result (导入结果)
  ↓ (用户点击"返回导入" 或 "查看通知书列表")
upload 或 notices
```

### 状态详解

| 状态 | 说明 | 显示内容 | 用户操作 |
|------|------|---------|---------|
| `upload` | 文件选择 | 文件上传区域 | 选择文件、导入 |
| `recognizing` | 识别中 | 加载动画 | 等待 |
| `preview-notices` | 预览通知书 | 通知书列表表格 | 选择、查看问题 |
| `preview-issues` | 预览问题 | 问题列表表格 | 编辑、选择、返回 |
| `confirm` | 确认导入 | 摘要信息 | 确认、取消 |
| `importing` | 导入中 | 进度条 | 等待 |
| `result` | 导入结果 | 结果反馈 | 返回、查看列表 |
| `notices` | 已导入列表 | 通知书列表 | 查看详情、删除 |

---

## 2. 前端状态管理详设

### importStore.js 完整状态定义

```javascript
// 识别结果缓存
const recognizedNotices = ref([])  // 识别的通知书列表
const recognizedIssues = ref([])   // 识别的问题列表
const currentRecognizedNoticeId = ref(null)  // 当前预览的通知书 ID

// 用户选择状态
const selectedNoticeIds = ref(new Set())  // 选中的通知书 ID
const selectedIssueIds = ref(new Set())   // 选中的问题 ID

// 编辑和验证状态
const editedData = ref({})         // 编辑的数据 {recordId: {...}}
const validationErrors = ref({})   // 验证错误 {recordId: [...]}
const modifiedRecords = ref(new Set())  // 已修改的记录 ID

// 导入流程状态
const importStep = ref(1)          // 当前步骤
const importProgress = ref(0)      // 导入进度 (0-100)
const importStartTime = ref(null)  // 导入开始时间

// 导入结果
const importResult = ref(null)     // 导入结果
const importErrors = ref([])       // 导入错误列表
```

### 新增 Action 方法

```javascript
// 识别阶段
const recognizeDocument = async (file) => {
  // 调用识别 API，缓存结果
}

// 预览阶段
const selectNoticeForPreview = (noticeId) => {
  // 切换预览的通知书
}

const toggleNoticeSelection = (noticeId) => {
  // 切换通知书选择状态
}

const toggleIssueSelection = (issueId) => {
  // 切换问题选择状态
}

// 编辑阶段
const editRecord = (recordId, fieldName, value) => {
  // 编辑记录字段
}

const validateRecord = (recordId) => {
  // 验证单条记录
}

const validateAllRecords = () => {
  // 验证所有记录
}

// 导入阶段
const importSelected = async () => {
  // 导入选中的记录
}

// 重置
const resetRecognition = () => {
  // 重置识别状态
}
```

---

## 3. 后端 API 设计

### API 1: 识别文档（修改现有）

**POST /api/import/document**

**修改说明**: 改为只识别不导入

**请求**:
```
Content-Type: multipart/form-data
file: <binary>
```

**响应**:
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
    "builder_unit": "云桂铁路广西有限责任公司",
    "issues_count": 65
  },
  "issues": [
    {
      "id": "temp_issue_1",
      "site_name": "工点 1",
      "description": "问题描述",
      "issue_category": "工程质量",
      "severity": 3,
      "rectification_deadline": "2025-09-20",
      "responsible_unit": "施工单位",
      "is_rectification_notice": true,
      "document_section": "rectification",
      ...更多字段
    }
  ]
}
```

### API 2: 导入选中的记录（新增）

**POST /api/notices/import-selected**

**请求**:
```json
{
  "notice": {
    "notice_number": "南宁站[2025]（通知）黄百10号",
    "check_date": "2025-08-20",
    "check_unit": "南宁监督站",
    "check_personnel": "李规录、陈胜",
    "project_name": "黄百铁路",
    "builder_unit": "云桂铁路广西有限责任公司"
  },
  "issues": [
    {
      "site_name": "工点 1",
      "description": "问题描述",
      "issue_category": "工程质量",
      "severity": 3,
      "rectification_deadline": "2025-09-20",
      "responsible_unit": "施工单位",
      "is_rectification_notice": true,
      ...更多字段
    }
  ]
}
```

**响应**:
```json
{
  "success": true,
  "notice_id": 123,
  "imported_issues_count": 65,
  "errors": []
}
```

---

## 4. 组件设计

### 新增组件列表

#### 1. ImportPreviewNotices.vue
- 显示识别的通知书列表
- 支持复选框选择
- 显示通知书基本信息
- "查看问题"按钮

#### 2. ImportPreviewIssues.vue
- 显示识别的问题列表
- 支持行内编辑
- 支持复选框选择
- 数据验证提示
- "返回"和"确认导入"按钮

#### 3. ImportConfirm.vue
- 显示导入摘要
- 显示选中的记录数量
- 显示验证状态
- "确认导入"和"取消"按钮

#### 4. ImportResult.vue
- 显示导入结果
- 显示成功/失败数量
- 显示错误详情
- "返回导入"和"查看通知书列表"按钮

---

## 5. 数据验证规则

### 通知书验证
- `notice_number`: 必填、长度 1-100
- `check_date`: 必填、日期格式
- `check_unit`: 必填、长度 1-100
- `project_name`: 必填、长度 1-100

### 问题验证
- `description`: 必填、长度 1-500
- `site_name`: 必填、长度 1-100
- `rectification_deadline`: 日期格式（可选）
- `responsible_unit`: 长度 1-100（可选）

### 冲突检测（可选）
- 检测通知书编号是否已存在
- 标记冲突记录

---

## 6. 性能优化策略

### 大数据处理
- 问题数 > 100: 使用虚拟滚动
- 问题数 > 500: 使用分页

### 编辑优化
- 实时保存到前端状态
- 防抖处理（300ms）
- 标记已修改记录

### 导入优化
- 批量插入（每 100 条一批）
- 显示进度条
- 后端使用事务处理

---

## 7. 错误处理

### 前端错误
- 文件格式错误
- 网络错误
- 验证错误

### 后端错误
- 识别失败
- 导入失败
- 数据库错误

### 用户提示
- 错误消息清晰
- 提供解决方案
- 支持重试

---

## 8. 用户交互流程

### 完整流程示例

1. **步骤 1**: 用户选择 Word 文件
2. **步骤 2**: 系统识别文件（显示加载动画）
3. **步骤 3**: 显示识别结果（通知书列表）
   - 用户可以查看通知书信息
   - 用户可以选择/取消选择通知书
   - 用户点击"查看问题"查看问题列表
4. **步骤 4**: 显示问题列表
   - 用户可以编辑问题字段
   - 用户可以选择/取消选择问题
   - 用户点击"返回"回到通知书列表
   - 用户点击"确认导入"进入确认界面
5. **步骤 5**: 显示导入确认
   - 显示选中的记录数量
   - 显示验证状态
   - 用户点击"确认导入"开始导入
6. **步骤 6**: 导入中（显示进度条）
7. **步骤 7**: 显示导入结果
   - 显示成功/失败数量
   - 显示错误详情
   - 用户可以返回或查看通知书列表

---

## 9. 代码复用策略

### 复用现有组件
- `IssuesTable.vue`: 行内编辑功能
- `NoticesListComponent.vue`: 列表展示
- `IssuesPreview.vue`: 问题预览

### 复用现有逻辑
- `importStore.js`: 状态管理
- `importService.js`: API 调用
- 数据验证逻辑

### 新增组件
- 预览组件（通知书、问题）
- 确认组件
- 结果反馈组件

---

## 10. 测试计划

### 单元测试
- 状态管理逻辑
- 数据验证逻辑
- API 调用

### 集成测试
- 完整导入流程
- 错误处理
- 边界情况

### 用户测试
- 用户体验
- 性能表现
- 数据准确性

