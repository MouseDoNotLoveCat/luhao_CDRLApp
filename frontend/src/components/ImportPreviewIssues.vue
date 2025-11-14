<template>
  <div class="import-preview-issues">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span class="title">📝 已识别的问题</span>
          <span class="subtitle">共 {{ issues.length }} 个</span>
        </div>
      </template>

      <!-- 统计信息 -->
      <div class="statistics">
        <el-statistic title="总问题数" :value="issues.length" />
        <el-statistic title="已选择" :value="selectedIssueIds.size" />
        <el-statistic title="下发整改通知单" :value="rectificationCount" />
        <el-statistic title="其他问题" :value="otherIssuesCount" />
      </div>

      <!-- 工具栏 -->
      <div class="toolbar">
        <el-checkbox v-model="selectAll" @change="handleSelectAll">
          全选/全不选
        </el-checkbox>
        <el-button type="primary" link @click="handleSelectRectification">
          选择下发整改通知单
        </el-button>
        <el-button type="primary" link @click="handleSelectOther">
          选择其他问题
        </el-button>
      </div>

      <!-- 问题列表 -->
      <el-table
        :data="issues"
        stripe
        border
        max-height="500px"
        @selection-change="handleTableSelectionChange"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="description" label="问题描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="site_name" label="工点" width="100" />
        <el-table-column prop="section_name" label="标段" width="100" />
        <el-table-column prop="document_section" label="来源" width="100">
          <template #default="{ row }">
            <el-tag :type="row.document_section === 'rectification' ? 'success' : 'info'">
              {{ row.document_section === 'rectification' ? '下发整改' : '其他问题' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <el-button @click="handleBack">返回</el-button>
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleConfirm" :disabled="selectedIssueIds.size === 0">
          下一步 ({{ selectedIssueIds.size }} 个已选)
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useImportStore } from '@/stores/importStore'
import { ElMessage } from 'element-plus'

const importStore = useImportStore()
const selectAll = ref(false)

const issues = computed(() => importStore.recognizedIssues)
const selectedIssueIds = computed(() => importStore.selectedIssueIds)

const rectificationCount = computed(() => 
  issues.value.filter(i => i.document_section === 'rectification').length
)

const otherIssuesCount = computed(() => 
  issues.value.filter(i => i.document_section === 'other').length
)

const handleSelectAll = (value) => {
  if (value) {
    issues.value.forEach((_, index) => {
      selectedIssueIds.value.add(index)
    })
  } else {
    selectedIssueIds.value.clear()
  }
}

const handleSelectRectification = () => {
  issues.value.forEach((issue, index) => {
    if (issue.document_section === 'rectification') {
      selectedIssueIds.value.add(index)
    }
  })
}

const handleSelectOther = () => {
  issues.value.forEach((issue, index) => {
    if (issue.document_section === 'other') {
      selectedIssueIds.value.add(index)
    }
  })
}

const handleBack = () => {
  importStore.previewNotices()
}

const handleCancel = () => {
  importStore.resetRecognition()
}

const handleConfirm = () => {
  if (selectedIssueIds.value.size === 0) {
    ElMessage.warning('请先选择至少一个问题')
    return
  }
  importStore.viewMode.value = 'confirm'
}

const handleTableSelectionChange = (selection) => {
  selectedIssueIds.value.clear()
  selection.forEach((row, index) => {
    const rowIndex = issues.value.findIndex(issue => issue.id === row.id)
    if (rowIndex !== -1) {
      selectedIssueIds.value.add(rowIndex)
    }
  })
}
</script>

<style scoped>
.import-preview-issues {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 16px;
  font-weight: bold;
}

.subtitle {
  color: #909399;
  font-size: 14px;
}

.statistics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  align-items: center;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
</style>

