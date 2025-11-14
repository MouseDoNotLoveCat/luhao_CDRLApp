<template>
  <div class="import-result">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span class="title">🎉 导入完成</span>
        </div>
      </template>

      <!-- 成功提示 -->
      <el-alert v-if="importResult.success" title="导入成功" type="success" :closable="false">
        <div class="result-content">
          <div class="result-item">
            <span class="label">通知书编号：</span>
            <span class="value">{{ importResult.notice_number }}</span>
          </div>
          <div class="result-item">
            <span class="label">导入的问题数：</span>
            <span class="value highlight">{{ importResult.imported_issues_count }}</span>
          </div>
        </div>
      </el-alert>

      <!-- 失败提示 -->
      <el-alert v-else title="导入失败" type="error" :closable="false">
        <div class="error-content">
          <p>{{ importResult.error }}</p>
        </div>
      </el-alert>

      <!-- 导入的问题列表 -->
      <div v-if="importResult.success && importResult.imported_issues" class="imported-issues">
        <h4>导入的问题列表</h4>
        <el-table :data="importResult.imported_issues" stripe border max-height="300px">
          <el-table-column prop="id" label="问题 ID" width="100" />
          <el-table-column prop="description" label="问题描述" min-width="200" show-overflow-tooltip />
        </el-table>
      </div>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <el-button @click="handleReturnToImport">返回导入</el-button>
        <el-button type="primary" @click="handleViewNotices">查看通知书列表</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useImportStore } from '@/stores/importStore'
import { useNoticeManagementStore } from '@/stores/noticeManagementStore'

const importStore = useImportStore()
const noticeStore = useNoticeManagementStore()

const importResult = computed(() => importStore.importResult || {})

const handleReturnToImport = () => {
  importStore.goBackToUpload()
}

const handleViewNotices = async () => {
  // 刷新通知书列表
  await noticeStore.fetchNotices()
  // 切换到通知书列表视图
  importStore.viewMode = 'notices'
}
</script>

<style scoped>
.import-result {
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

.result-content {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  padding: 10px 0;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.label {
  font-weight: bold;
  color: #606266;
  min-width: 100px;
}

.value {
  color: #303133;
}

.value.highlight {
  color: #67c23a;
  font-weight: bold;
  font-size: 16px;
}

.error-content {
  padding: 10px 0;
}

.error-content p {
  margin: 0;
  color: #f56c6c;
}

.imported-issues {
  margin-top: 20px;
  margin-bottom: 20px;
}

.imported-issues h4 {
  margin-bottom: 10px;
  color: #303133;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
</style>

