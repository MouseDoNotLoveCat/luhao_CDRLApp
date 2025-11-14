<template>
  <div class="import-page">
    <!-- 第一层：上传界面 -->
    <div v-if="importStore.viewMode === 'upload'" class="import-container">
      <!-- 步骤 1: 文件选择 -->
      <div class="import-section">
        <h2 class="section-title">📄 步骤 1: 选择监督检查通知书</h2>
        <p class="section-description">支持单个或多个 .docx 文件，系统将自动判断使用相应的导入方式</p>

        <div class="file-upload-area" @dragover.prevent @drop.prevent="handleFileDrop">
          <div class="upload-icon">📁</div>
          <p class="upload-text">拖拽 .docx 文件到此处或点击选择</p>
          <input
            ref="fileInput"
            type="file"
            accept=".docx"
            multiple
            @change="handleFileSelect"
            style="display: none"
          >
          <el-button type="primary" @click="$refs.fileInput.click()">
            选择文件
          </el-button>
        </div>

        <!-- 已选择的文件列表 -->
        <div v-if="importStore.hasFiles" class="files-info">
          <div class="files-header">
            <div class="files-summary">
              <span class="file-count">已选择 {{ importStore.filesCount }} 个文件</span>
              <span class="file-size">总大小 {{ importStore.totalFilesSize }}</span>
            </div>
            <el-button link @click="importStore.clearSelectedFiles()">
              清空
            </el-button>
          </div>
          <div class="files-list">
            <div v-for="(file, index) in importStore.selectedFiles" :key="index" class="file-item">
              <span class="file-icon">📄</span>
              <span class="file-name">{{ file.name }}</span>
              <span class="file-size">{{ formatFileSize(file.size) }}</span>
              <el-button link @click="importStore.removeSelectedFile(index)">
                移除
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 步骤 2: 导入按钮 -->
      <div class="import-section">
        <h2 class="section-title">⚙️ 步骤 2: 开始导入</h2>

        <div class="import-actions">
          <el-button
            type="primary"
            size="large"
            :loading="isImporting"
            :disabled="!importStore.hasFiles"
            @click="handleImport"
          >
            <span v-if="!isImporting">
              {{ importStore.filesCount === 1 ? '导入文件' : '批量导入' }}
            </span>
            <span v-else>
              {{ importStore.filesCount === 1 ? '导入中...' : '批量导入中...' }}
            </span>
          </el-button>
          <span v-if="importStore.hasFiles" class="import-hint">
            {{ importStore.filesCount === 1 ? '将使用单文件导入' : `将使用批量导入 (${importStore.filesCount} 个文件)` }}
          </span>
        </div>

        <!-- 导入进度条 -->
        <div v-if="isImporting" style="margin-top: 16px">
          <el-progress :percentage="importProgress" />
        </div>

        <!-- 错误提示 -->
        <el-alert
          v-if="importStore.error"
          type="error"
          :title="importStore.error"
          closable
          @close="importStore.error = null"
          style="margin-top: 16px"
        />
      </div>

      <!-- 步骤 3: 导入结果 (单文件) -->
      <div v-if="importStore.importResult && importStore.filesCount === 1" class="import-section">
        <h2 class="section-title">✅ 步骤 3: 导入结果</h2>

        <el-card class="result-card">
          <template #header>
            <div class="card-header">
              <span>✅ 导入成功</span>
            </div>
          </template>

          <div class="result-info">
            <div class="info-row">
              <span class="label">通知书编号:</span>
              <span class="value">{{ importStore.importResult.notice_number }}</span>
            </div>
            <div class="info-row">
              <span class="label">检查日期:</span>
              <span class="value">{{ importStore.importResult.check_date }}</span>
            </div>
            <div class="info-row">
              <span class="label">检查单位:</span>
              <span class="value">{{ importStore.importResult.check_unit }}</span>
            </div>
            <div class="info-row">
              <span class="label">检查人员:</span>
              <span class="value">{{ importStore.importResult.check_personnel }}</span>
            </div>
            <div class="info-row">
              <span class="label">项目名称:</span>
              <span class="value">{{ importStore.importResult.project_name }}</span>
            </div>
            <div class="info-row">
              <span class="label">建设单位:</span>
              <span class="value">{{ importStore.importResult.builder_unit }}</span>
            </div>
          </div>

          <el-divider />

          <div class="issues-summary">
            <h3>问题统计</h3>
            <div class="summary-grid">
              <div class="summary-item">
                <div class="summary-label">质量问题</div>
                <div class="summary-value">{{ importStore.importResult.quality_issues_count }}</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">安全问题</div>
                <div class="summary-value">{{ importStore.importResult.safety_issues_count }}</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">管理问题</div>
                <div class="summary-value">{{ importStore.importResult.management_issues_count }}</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">问题总数</div>
                <div class="summary-value total">{{ importStore.importResult.total_issues_count }}</div>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 步骤 3: 批量导入结果 -->
      <div v-if="importStore.batchImportResult && importStore.filesCount > 1" class="import-section">
        <h2 class="section-title">✅ 步骤 3: 批量导入结果</h2>

        <el-card class="result-card">
          <template #header>
            <div class="card-header">
              <span v-if="importStore.batchImportResult.failed === 0">✅ 全部导入成功</span>
              <span v-else>⚠️ 部分导入失败</span>
            </div>
          </template>

          <div class="result-info">
            <div class="info-row">
              <span class="label">总文件数:</span>
              <span class="value">{{ importStore.batchImportResult.total_files }}</span>
            </div>
            <div class="info-row">
              <span class="label">成功导入:</span>
              <span class="value success">{{ importStore.batchImportResult.successful }}</span>
            </div>
            <div class="info-row">
              <span class="label">导入失败:</span>
              <span class="value error">{{ importStore.batchImportResult.failed }}</span>
            </div>
            <div class="info-row">
              <span class="label">问题总数:</span>
              <span class="value">{{ importStore.batchImportResult.total_issues }}</span>
            </div>
          </div>

          <!-- 详细结果 -->
          <div v-if="importStore.batchImportResult.details" class="batch-details">
            <h4>详细结果</h4>
            <div class="details-list">
              <div v-for="(detail, index) in importStore.batchImportResult.details" :key="index" class="detail-item">
                <div class="detail-header">
                  <span v-if="detail.success" class="status success">✓</span>
                  <span v-else class="status error">✗</span>
                  <span class="file-name">{{ detail.file_name }}</span>
                </div>
                <div v-if="detail.success" class="detail-content">
                  <span>通知书编号: {{ detail.notice_number }}</span>
                  <span>问题数: {{ detail.total_issues }}</span>
                </div>
                <div v-else class="detail-content error">
                  <span>错误: {{ detail.error }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 步骤 4: 问题一览表 -->
      <div v-if="importStore.issues.length > 0" class="import-section">
        <h2 class="section-title">📋 步骤 4: 问题一览表</h2>

        <IssuesTable
          :issues="importStore.issues"
          @row-click="handleIssueClick"
        />
      </div>
    </div>

    <!-- 新增：识别中 -->
    <div v-else-if="importStore.viewMode === 'recognizing'" class="import-container">
      <el-card class="box-card">
        <template #header>
          <div class="card-header">
            <span>🔄 正在识别文件...</span>
          </div>
        </template>
        <el-progress :percentage="50" :indeterminate="true" />
      </el-card>
    </div>

    <!-- 新增：预览通知书 -->
    <div v-else-if="importStore.viewMode === 'preview-notices'">
      <ImportPreviewNotices />
    </div>

    <!-- 新增：预览问题 -->
    <div v-else-if="importStore.viewMode === 'preview-issues'">
      <ImportPreviewIssues />
    </div>

    <!-- 新增：确认导入 -->
    <div v-else-if="importStore.viewMode === 'confirm'">
      <ImportConfirm />
    </div>

    <!-- 新增：导入中 -->
    <div v-else-if="importStore.viewMode === 'importing'" class="import-container">
      <el-card class="box-card">
        <template #header>
          <div class="card-header">
            <span>⏳ 正在导入...</span>
          </div>
        </template>
        <el-progress :percentage="importStore.importProgress" />
      </el-card>
    </div>

    <!-- 新增：导入结果 -->
    <div v-else-if="importStore.viewMode === 'result'">
      <ImportResult />
    </div>

    <!-- 第二层：通知书列表 -->
    <div v-else-if="importStore.viewMode === 'notices'">
      <NoticesListComponent />
    </div>

    <!-- 第三层：问题一览表 -->
    <div v-else-if="importStore.viewMode === 'issues'">
      <IssuesPreview />
    </div>

    <!-- 第四层：问题详情 -->
    <div v-else-if="importStore.viewMode === 'detail'">
      <IssueDetailPreview />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useImportStore } from '../stores/importStore'
import { useNoticeManagementStore } from '../stores/noticeManagementStore'
import IssuesTable from '../components/IssuesTable.vue'
import NoticesListComponent from '../components/NoticesListComponent.vue'
import IssuesPreview from '../components/IssuesPreview.vue'
import IssueDetailPreview from '../components/IssueDetailPreview.vue'
import ImportPreviewNotices from '../components/ImportPreviewNotices.vue'
import ImportPreviewIssues from '../components/ImportPreviewIssues.vue'
import ImportConfirm from '../components/ImportConfirm.vue'
import ImportResult from '../components/ImportResult.vue'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['show-detail'])

const importStore = useImportStore()
const noticeStore = useNoticeManagementStore()
const fileInput = ref(null)

// 计算导入状态
const isImporting = computed(() => {
  return importStore.isLoading || importStore.isBatchLoading
})

// 计算导入进度
const importProgress = computed(() => {
  if (importStore.isLoading) {
    return 50  // 单文件导入显示 50%
  }
  return importStore.batchProgress
})

// 处理文件选择
const handleFileSelect = (event) => {
  const files = event.target.files
  if (files && files.length > 0) {
    // 验证所有文件都是 .docx 格式
    const invalidFiles = Array.from(files).filter(f => !f.name.endsWith('.docx'))
    if (invalidFiles.length > 0) {
      ElMessage.error('请只选择 .docx 格式的文件')
      return
    }
    importStore.setSelectedFiles(files)
  }
}

// 处理拖拽
const handleFileDrop = (event) => {
  const files = event.dataTransfer.files
  if (files && files.length > 0) {
    // 验证所有文件都是 .docx 格式
    const invalidFiles = Array.from(files).filter(f => !f.name.endsWith('.docx'))
    if (invalidFiles.length > 0) {
      ElMessage.error('请只选择 .docx 格式的文件')
      return
    }
    importStore.setSelectedFiles(files)
  }
}

// 统一导入处理 - 改为识别而不是直接导入
const handleImport = async () => {
  const success = await importStore.recognizeDocument()
  if (success) {
    ElMessage.success('文件识别成功，请预览并选择要导入的内容')
  }
}

// 处理问题点击
const handleIssueClick = (issue) => {
  console.log('🔴 ImportPage: handleIssueClick 被触发，issue:', issue)
  console.log('📍 准备发送 show-detail 事件，issueId:', issue.id)
  emit('show-detail', issue.id)
  console.log('✅ 已发送 show-detail 事件')
}

// 格式化文件大小
const formatFileSize = (size) => {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(2)} KB`
  return `${(size / (1024 * 1024)).toFixed(2)} MB`
}
</script>

<style scoped>
.import-page {
  max-width: 1200px;
  margin: 0 auto;
}

.import-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.import-section {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
}

.section-description {
  font-size: 13px;
  color: #999;
  margin-bottom: 16px;
}

.file-upload-area {
  border: 2px dashed #667eea;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  background-color: #f9f9ff;
  transition: all 0.3s ease;
  cursor: pointer;
}

.file-upload-area:hover {
  border-color: #764ba2;
  background-color: #f5f0ff;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.upload-text {
  color: #666;
  margin-bottom: 16px;
  font-size: 14px;
}

.files-info {
  margin-top: 16px;
  padding: 12px;
  background-color: #f0f4ff;
  border-radius: 4px;
}

.files-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.files-summary {
  display: flex;
  gap: 16px;
  font-weight: 500;
  color: #333;
}

.file-count {
  color: #667eea;
  font-weight: 600;
}

.file-size {
  color: #999;
  font-size: 13px;
}

.files-list {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background: white;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-bottom: 1px solid #f0f0f0;
}

.file-item:last-child {
  border-bottom: none;
}

.file-icon {
  margin-right: 8px;
  font-size: 14px;
}

.file-name {
  flex: 1;
  color: #333;
  font-size: 14px;
  word-break: break-all;
}

.import-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.import-hint {
  font-size: 13px;
  color: #999;
}

.result-card {
  margin-top: 16px;
}

.card-header {
  font-weight: 600;
  color: #333;
}

.result-info {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.info-row {
  display: flex;
  align-items: center;
}

.label {
  color: #666;
  font-weight: 500;
  min-width: 100px;
}

.value {
  color: #333;
  flex: 1;
}

.issues-summary {
  margin-top: 16px;
}

.issues-summary h3 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #333;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.summary-item {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px;
  border-radius: 8px;
  text-align: center;
}

.summary-item.total {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.summary-label {
  font-size: 12px;
  opacity: 0.9;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 24px;
  font-weight: 700;
}

/* 批量导入详细结果样式 */
.batch-details {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
}

.batch-details h4 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #333;
}

.details-list {
  max-height: 400px;
  overflow-y: auto;
}

.detail-item {
  padding: 12px;
  margin-bottom: 8px;
  background: #f9f9f9;
  border-radius: 4px;
  border-left: 3px solid #667eea;
}

.detail-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.status {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  margin-right: 8px;
  font-weight: bold;
  color: white;
}

.status.success {
  background-color: #67c23a;
}

.status.error {
  background-color: #f56c6c;
}

.detail-header .file-name {
  flex: 1;
  color: #333;
  font-weight: 500;
}

.detail-content {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #666;
}

.detail-content.error {
  color: #f56c6c;
}

.value.success {
  color: #67c23a;
  font-weight: 600;
}

.value.error {
  color: #f56c6c;
  font-weight: 600;
}

@media (max-width: 768px) {
  .result-info {
    grid-template-columns: 1fr;
  }

  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .file-upload-area {
    padding: 24px;
  }

  .files-list {
    max-height: 200px;
  }

  .details-list {
    max-height: 300px;
  }

  .files-summary {
    flex-direction: column;
    gap: 4px;
  }
}
</style>

