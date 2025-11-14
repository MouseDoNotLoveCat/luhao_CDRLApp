<template>
  <div class="import-preview-notices">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span class="title">📋 已识别的通知书</span>
          <span class="subtitle">共 {{ recognizedNotices.length }} 份</span>
        </div>
      </template>

      <!-- 通知书列表 -->
      <el-table
        ref="tableRef"
        :data="recognizedNotices"
        stripe
        border
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="notice_number" label="通知书编号" width="150" />
        <el-table-column prop="check_date" label="检查日期" width="120" />
        <el-table-column prop="check_unit" label="检查单位" width="150" />
        <el-table-column prop="total_issues_count" label="问题数量" width="100" align="center" />
        <el-table-column label="操作" width="200" align="center">
          <template #default="{ row, $index }">
            <el-button type="primary" link @click="handleViewIssues($index)">
              查看问题
            </el-button>
            <el-button type="danger" link @click="handleRemove($index)">
              移除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleNext" :disabled="selectedNotices.length === 0">
          下一步 ({{ selectedNotices.length }} 份已选)
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
const tableRef = ref(null)

const recognizedNotices = computed(() => importStore.recognizedNotices)

const selectedNotices = computed(() => {
  return recognizedNotices.value.filter((_, index) => 
    importStore.selectedNoticeIds.has(index)
  )
})

const handleViewIssues = (index) => {
  // 设置当前预览的通知书索引
  importStore.currentRecognizedNoticeId = index
  // 转到问题预览界面
  importStore.previewIssues()
}

const handleRemove = (index) => {
  // 从识别的通知书列表中移除
  recognizedNotices.value.splice(index, 1)
  // 如果没有通知书了，返回上传界面
  if (recognizedNotices.value.length === 0) {
    importStore.goBackToUpload()
  }
}

const handleCancel = () => {
  importStore.resetRecognition()
}

const handleNext = () => {
  if (selectedNotices.value.length === 0) {
    ElMessage.warning('请先选择至少一份通知书')
    return
  }
  importStore.previewIssues()
}

// 处理表格选择
const handleSelectionChange = (selection) => {
  importStore.selectedNoticeIds.value.clear()
  selection.forEach((row, index) => {
    importStore.selectedNoticeIds.value.add(index)
  })
}
</script>

<style scoped>
.import-preview-notices {
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

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
</style>

