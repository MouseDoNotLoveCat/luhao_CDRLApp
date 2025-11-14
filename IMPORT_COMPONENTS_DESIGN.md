# CDRLApp 导入功能 - 组件设计文档

## 1. ImportPreviewNotices.vue

### 功能
- 显示识别的通知书列表
- 支持复选框选择
- 显示通知书基本信息
- "查看问题"按钮

### Props
```javascript
// 无 props，直接使用 importStore
```

### 数据
```javascript
const importStore = useImportStore()

// 计算属性
const allNoticesSelected = computed(() => {
  return importStore.recognizedNotices.length > 0 &&
    importStore.recognizedNotices.every(n => 
      importStore.selectedNoticeIds.has(n.id)
    )
})

const selectedCount = computed(() => {
  return importStore.selectedNoticeIds.size
})
```

### 方法
```javascript
const toggleNoticeSelection = (noticeId) => {
  if (importStore.selectedNoticeIds.has(noticeId)) {
    importStore.selectedNoticeIds.delete(noticeId)
  } else {
    importStore.selectedNoticeIds.add(noticeId)
  }
}

const toggleAllNotices = () => {
  if (allNoticesSelected.value) {
    importStore.selectedNoticeIds.clear()
  } else {
    importStore.recognizedNotices.forEach(n => {
      importStore.selectedNoticeIds.add(n.id)
    })
  }
}

const viewProblems = (notice) => {
  importStore.currentRecognizedNoticeId = notice.id
  importStore.viewMode = 'preview-issues'
}

const goBack = () => {
  importStore.viewMode = 'upload'
}
```

### 模板
```vue
<template>
  <div class="preview-notices">
    <h2>步骤 3: 确认识别结果</h2>
    
    <!-- 操作栏 -->
    <div class="toolbar">
      <el-checkbox 
        :model-value="allNoticesSelected"
        @change="toggleAllNotices"
      >
        全选 ({{ selectedCount }}/{{ importStore.recognizedNotices.length }})
      </el-checkbox>
      <el-button @click="goBack">返回</el-button>
    </div>

    <!-- 通知书表格 -->
    <el-table :data="importStore.recognizedNotices">
      <el-table-column width="50">
        <template #default="{ row }">
          <el-checkbox 
            :model-value="importStore.selectedNoticeIds.has(row.id)"
            @change="toggleNoticeSelection(row.id)"
          />
        </template>
      </el-table-column>
      <el-table-column prop="notice_number" label="通知书编号" />
      <el-table-column prop="check_date" label="检查日期" />
      <el-table-column prop="check_unit" label="检查单位" />
      <el-table-column prop="issues_count" label="问题数量" />
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button 
            type="primary" 
            size="small"
            @click="viewProblems(row)"
          >
            查看问题
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 操作按钮 -->
    <div class="actions">
      <el-button @click="goBack">返回</el-button>
      <el-button 
        type="primary"
        :disabled="selectedCount === 0"
        @click="confirmImport"
      >
        确认导入 ({{ selectedCount }} 个通知书)
      </el-button>
    </div>
  </div>
</template>
```

---

## 2. ImportPreviewIssues.vue

### 功能
- 显示识别的问题列表
- 支持行内编辑
- 支持复选框选择
- 数据验证提示

### Props
```javascript
// 无 props，直接使用 importStore
```

### 数据
```javascript
const importStore = useImportStore()

// 当前通知书的问题列表
const currentIssues = computed(() => {
  return importStore.recognizedIssues.filter(
    issue => issue.notice_id === importStore.currentRecognizedNoticeId
  )
})

// 编辑状态
const editingId = ref(null)
const editingField = ref(null)
const editingValue = ref(null)
```

### 方法
```javascript
const toggleIssueSelection = (issueId) => {
  if (importStore.selectedIssueIds.has(issueId)) {
    importStore.selectedIssueIds.delete(issueId)
  } else {
    importStore.selectedIssueIds.add(issueId)
  }
}

const startEdit = (issue, field) => {
  editingId.value = issue.id
  editingField.value = field
  editingValue.value = issue[field]
}

const saveEdit = (issue, field) => {
  // 更新 editedData
  if (!importStore.editedData[issue.id]) {
    importStore.editedData[issue.id] = {}
  }
  importStore.editedData[issue.id][field] = editingValue.value
  
  // 更新原始数据
  issue[field] = editingValue.value
  
  // 标记为已修改
  importStore.modifiedRecords.add(issue.id)
  
  // 验证
  validateRecord(issue)
  
  editingId.value = null
}

const validateRecord = (issue) => {
  const errors = []
  if (!issue.description) errors.push('问题描述必填')
  if (!issue.site_name) errors.push('工点名称必填')
  
  if (errors.length > 0) {
    importStore.validationErrors[issue.id] = errors
  } else {
    delete importStore.validationErrors[issue.id]
  }
}

const goBack = () => {
  importStore.viewMode = 'preview-notices'
}

const confirmImport = () => {
  // 验证所有记录
  let hasErrors = false
  currentIssues.value.forEach(issue => {
    validateRecord(issue)
    if (importStore.validationErrors[issue.id]) {
      hasErrors = true
    }
  })
  
  if (hasErrors) {
    ElMessage.error('存在验证错误，请修正后再导入')
    return
  }
  
  importStore.viewMode = 'confirm'
}
```

### 模板
```vue
<template>
  <div class="preview-issues">
    <h2>步骤 3: 确认问题列表</h2>
    
    <!-- 问题表格 -->
    <el-table :data="currentIssues">
      <el-table-column width="50">
        <template #default="{ row }">
          <el-checkbox 
            :model-value="importStore.selectedIssueIds.has(row.id)"
            @change="toggleIssueSelection(row.id)"
          />
        </template>
      </el-table-column>
      
      <!-- 问题描述 -->
      <el-table-column prop="description" label="问题描述" min-width="150">
        <template #default="{ row }">
          <template v-if="editingId === row.id && editingField === 'description'">
            <el-input 
              v-model="editingValue"
              type="textarea"
              @blur="saveEdit(row, 'description')"
            />
          </template>
          <template v-else>
            <span 
              @click="startEdit(row, 'description')"
              style="cursor: pointer; color: #409eff"
            >
              {{ row.description }}
            </span>
          </template>
        </template>
      </el-table-column>
      
      <!-- 工点名称 -->
      <el-table-column prop="site_name" label="工点名称" width="120">
        <template #default="{ row }">
          <template v-if="editingId === row.id && editingField === 'site_name'">
            <el-input 
              v-model="editingValue"
              @blur="saveEdit(row, 'site_name')"
            />
          </template>
          <template v-else>
            <span 
              @click="startEdit(row, 'site_name')"
              style="cursor: pointer; color: #409eff"
            >
              {{ row.site_name }}
            </span>
          </template>
        </template>
      </el-table-column>
      
      <!-- 更多字段... -->
      
      <!-- 验证错误提示 -->
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag 
            v-if="importStore.validationErrors[row.id]"
            type="danger"
          >
            有错误
          </el-tag>
          <el-tag 
            v-else-if="importStore.modifiedRecords.has(row.id)"
            type="warning"
          >
            已修改
          </el-tag>
          <el-tag v-else type="success">正常</el-tag>
        </template>
      </el-table-column>
    </el-table>

    <!-- 操作按钮 -->
    <div class="actions">
      <el-button @click="goBack">返回</el-button>
      <el-button 
        type="primary"
        @click="confirmImport"
      >
        确认导入
      </el-button>
    </div>
  </div>
</template>
```

---

## 3. ImportConfirm.vue

### 功能
- 显示导入摘要
- 显示选中的记录数量
- 显示验证状态

### 模板
```vue
<template>
  <div class="import-confirm">
    <h2>步骤 4: 确认导入</h2>
    
    <!-- 摘要信息 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>导入摘要</span>
        </div>
      </template>
      
      <div class="summary">
        <div class="summary-item">
          <span class="label">选中的通知书:</span>
          <span class="value">{{ selectedNoticeCount }} 个</span>
        </div>
        <div class="summary-item">
          <span class="label">选中的问题:</span>
          <span class="value">{{ selectedIssueCount }} 个</span>
        </div>
        <div class="summary-item">
          <span class="label">验证状态:</span>
          <el-tag 
            :type="hasErrors ? 'danger' : 'success'"
          >
            {{ hasErrors ? '有错误' : '通过' }}
          </el-tag>
        </div>
      </div>
    </el-card>

    <!-- 操作按钮 -->
    <div class="actions">
      <el-button @click="cancel">取消</el-button>
      <el-button 
        type="primary"
        :disabled="hasErrors"
        @click="confirmImport"
      >
        确认导入
      </el-button>
    </div>
  </div>
</template>
```

---

## 4. ImportResult.vue

### 功能
- 显示导入结果
- 显示成功/失败数量
- 显示错误详情

### 模板
```vue
<template>
  <div class="import-result">
    <h2>步骤 5: 导入完成</h2>
    
    <!-- 结果摘要 -->
    <el-result 
      :icon="importStore.importResult.success ? 'success' : 'error'"
      :title="importStore.importResult.success ? '导入成功' : '导入失败'"
    >
      <template #sub-title>
        <div v-if="importStore.importResult.success">
          成功导入 {{ importStore.importResult.imported_issues_count }} 个问题
        </div>
        <div v-else>
          {{ importStore.importResult.error }}
        </div>
      </template>
    </el-result>

    <!-- 错误详情 -->
    <div v-if="importStore.importErrors.length > 0" class="error-details">
      <h3>错误详情</h3>
      <el-table :data="importStore.importErrors">
        <el-table-column prop="record_id" label="记录 ID" />
        <el-table-column prop="error" label="错误信息" />
      </el-table>
    </div>

    <!-- 操作按钮 -->
    <div class="actions">
      <el-button @click="goBack">返回导入</el-button>
      <el-button 
        type="primary"
        @click="viewNoticesList"
      >
        查看通知书列表
      </el-button>
    </div>
  </div>
</template>
```

---

## 5. 组件集成到 ImportPage.vue

### 修改内容
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
      <!-- 原有的文件选择界面 -->
    </div>
    <div v-else-if="importStore.viewMode === 'recognizing'">
      <el-skeleton :rows="5" animated />
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
      <el-progress :percentage="importStore.importProgress" />
    </div>
    <div v-else-if="importStore.viewMode === 'result'">
      <ImportResult />
    </div>
  </div>
</template>

<script setup>
import ImportPreviewNotices from '../components/ImportPreviewNotices.vue'
import ImportPreviewIssues from '../components/ImportPreviewIssues.vue'
import ImportConfirm from '../components/ImportConfirm.vue'
import ImportResult from '../components/ImportResult.vue'
</script>
```

---

## 6. 样式指南

### 通用样式
```css
.import-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #dcdfe6;
}

.summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.summary-item .label {
  font-weight: 500;
  color: #606266;
}

.summary-item .value {
  font-size: 18px;
  font-weight: bold;
  color: #409eff;
}
```

