# CDRLApp 导入功能改造 - 实施指南

## 📋 实施步骤概览

### 第 1 阶段：后端 API 改造（1-2 天）

#### 步骤 1.1: 修改识别 API

**文件**: `backend/app/services/import_service.py`

**修改内容**:
- 修改 `import_word_document()` 方法
- 改为只识别不导入数据库
- 返回识别结果（通知书 + 问题列表）

**关键代码**:
```python
def import_word_document(self, file_path: str) -> Dict:
    # 解析文档
    parse_result = parse_word_document(file_path)
    
    # 返回识别结果（不导入数据库）
    return {
        'success': True,
        'notice': {
            'id': 'temp_' + str(uuid.uuid4()),
            'notice_number': parse_result['notice_number'],
            'check_date': parse_result['check_date'],
            'check_unit': parse_result['check_unit'],
            'check_personnel': parse_result['check_personnel'],
            'project_name': parse_result['project_name'],
            'builder_unit': parse_result['builder_unit'],
            'issues_count': len(parse_result['rectification_notices']) + len(parse_result['other_issues'])
        },
        'issues': [
            # 返回所有问题（包括整改通知单和其他问题）
        ]
    }
```

#### 步骤 1.2: 新增导入 API

**文件**: `backend/app/main.py`

**新增端点**:
```python
@app.post("/api/notices/import-selected")
async def import_selected(data: dict):
    """导入选中的通知书和问题"""
    service = ImportService(str(DB_PATH))
    result = service.import_selected_records(data)
    return result
```

**文件**: `backend/app/services/import_service.py`

**新增方法**:
```python
def import_selected_records(self, data: Dict) -> Dict:
    """导入选中的通知书和问题"""
    try:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 开启事务
        cursor.execute("BEGIN TRANSACTION")
        
        # 1. 插入通知书
        notice_id = self._insert_supervision_notice(cursor, data['notice'])
        
        # 2. 插入项目和标段
        project_result = self._insert_project(cursor, data['notice'])
        project_id = project_result['id']
        
        # 3. 插入问题
        imported_count = 0
        for issue in data['issues']:
            issue_id = self._insert_issue(cursor, notice_id, issue, project_id)
            if issue_id:
                imported_count += 1
        
        # 提交事务
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'notice_id': notice_id,
            'imported_issues_count': imported_count,
            'errors': []
        }
    except Exception as e:
        conn.rollback()
        conn.close()
        return {
            'success': False,
            'error': str(e)
        }
```

---

### 第 2 阶段：前端状态管理（1 天）

#### 步骤 2.1: 扩展 importStore.js

**文件**: `frontend/src/stores/importStore.js`

**新增状态**:
```javascript
// 识别结果缓存
const recognizedNotices = ref([])
const recognizedIssues = ref([])
const currentRecognizedNoticeId = ref(null)

// 用户选择状态
const selectedNoticeIds = ref(new Set())
const selectedIssueIds = ref(new Set())

// 编辑和验证状态
const editedData = ref({})
const validationErrors = ref({})
const modifiedRecords = ref(new Set())

// 导入流程状态
const importStep = ref(1)
const importProgress = ref(0)
```

**新增方法**:
```javascript
// 识别文档
const recognizeDocument = async (file) => {
  isLoading.value = true
  try {
    const result = await importService.importDocument(file)
    recognizedNotices.value = [result.notice]
    recognizedIssues.value = result.issues
    viewMode.value = 'preview-notices'
    return true
  } catch (err) {
    error.value = err.message
    return false
  } finally {
    isLoading.value = false
  }
}

// 导入选中的记录
const importSelected = async () => {
  importProgress.value = 0
  try {
    const selectedIssues = recognizedIssues.value.filter(
      issue => selectedIssueIds.value.has(issue.id)
    )
    
    const result = await importService.importSelected({
      notice: recognizedNotices.value[0],
      issues: selectedIssues
    })
    
    importProgress.value = 100
    return result
  } catch (err) {
    error.value = err.message
    return null
  }
}
```

---

### 第 3 阶段：前端 UI 组件（2-3 天）

#### 步骤 3.1: 创建预览组件

**新文件**: `frontend/src/components/ImportPreviewNotices.vue`

**功能**:
- 显示识别的通知书列表
- 支持复选框选择
- "查看问题"按钮

**新文件**: `frontend/src/components/ImportPreviewIssues.vue`

**功能**:
- 显示识别的问题列表
- 支持行内编辑
- 支持复选框选择
- 数据验证提示

#### 步骤 3.2: 创建确认和结果组件

**新文件**: `frontend/src/components/ImportConfirm.vue`

**功能**:
- 显示导入摘要
- 显示选中的记录数量
- 显示验证状态

**新文件**: `frontend/src/components/ImportResult.vue`

**功能**:
- 显示导入结果
- 显示成功/失败数量
- 显示错误详情

#### 步骤 3.3: 修改 ImportPage.vue

**修改内容**:
- 添加新的 viewMode 值处理
- 集成新的组件
- 添加步骤指示器

**关键代码**:
```vue
<template>
  <div class="import-page">
    <!-- 步骤指示器 -->
    <el-steps :active="importStep" finish-status="success">
      <el-step title="选择文件" />
      <el-step title="识别中" />
      <el-step title="确认结果" />
      <el-step title="导入中" />
      <el-step title="完成" />
    </el-steps>

    <!-- 各个视图 -->
    <div v-if="importStore.viewMode === 'upload'">
      <!-- 文件选择界面 -->
    </div>
    <div v-else-if="importStore.viewMode === 'recognizing'">
      <!-- 识别中 -->
    </div>
    <div v-else-if="importStore.viewMode === 'preview-notices'">
      <ImportPreviewNotices />
    </div>
    <div v-else-if="importStore.viewMode === 'preview-issues'">
      <ImportPreviewIssues />
    </div>
    <div v-else-if="importStore.viewMode === 'confirm'">
      <ImportConfirm />
    </div>
    <div v-else-if="importStore.viewMode === 'importing'">
      <!-- 导入中 -->
    </div>
    <div v-else-if="importStore.viewMode === 'result'">
      <ImportResult />
    </div>
  </div>
</template>
```

---

### 第 4 阶段：测试和优化（1-2 天）

#### 步骤 4.1: 单元测试
- 测试状态管理逻辑
- 测试数据验证逻辑
- 测试 API 调用

#### 步骤 4.2: 集成测试
- 测试完整导入流程
- 测试错误处理
- 测试边界情况

#### 步骤 4.3: 性能优化
- 优化大数据处理
- 优化编辑操作
- 优化导入速度

---

## 🔄 向后兼容性保证

### 保持现有功能
- ✅ 保持 `importedNotices` 状态
- ✅ 保持 `noticeIssues` 状态
- ✅ 保持导航方法（`goToNoticesList` 等）
- ✅ 保持通知书管理功能

### 迁移策略
- 新流程使用新的状态和方法
- 旧流程继续使用旧的状态和方法
- 逐步迁移用户到新流程

---

## 📊 工作量估算

| 任务 | 工作量 | 时间 |
|------|--------|------|
| 后端 API 改造 | 中 | 1-2 天 |
| 前端状态管理 | 中 | 1 天 |
| 前端 UI 组件 | 大 | 2-3 天 |
| 测试和优化 | 中 | 1-2 天 |
| **总计** | **大** | **5-8 天** |

---

## ✅ 验收清单

- [ ] 后端 API 改造完成
- [ ] 前端状态管理扩展完成
- [ ] 预览组件创建完成
- [ ] 确认和结果组件创建完成
- [ ] ImportPage.vue 集成完成
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 性能测试通过
- [ ] 用户体验测试通过
- [ ] 向后兼容性验证通过

---

## 🚀 后续优化

1. **冲突检测**: 检测通知书编号是否重复
2. **异步处理**: 大量数据导入时使用后台任务
3. **导入历史**: 记录导入历史和操作日志
4. **数据对比**: 显示新导入数据与已有数据的差异
5. **模板导出**: 支持导出识别结果为 Excel

