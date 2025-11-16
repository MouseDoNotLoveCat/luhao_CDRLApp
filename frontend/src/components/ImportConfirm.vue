<template>
  <div class="import-confirm">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span class="title">✅ 确认导入</span>
        </div>
      </template>

      <!-- 导入摘要 -->
      <div class="summary">
        <el-alert title="导入摘要" type="info" :closable="false">
          <div class="summary-content">
            <div class="summary-item">
              <span class="label">通知书编号：</span>
              <span class="value">{{ currentNotice.notice_number }}</span>
            </div>
            <div class="summary-item">
              <span class="label">检查日期：</span>
              <span class="value">{{ currentNotice.check_date }}</span>
            </div>
            <div class="summary-item">
              <span class="label">检查单位：</span>
              <span class="value">{{ currentNotice.check_unit }}</span>
            </div>
            <div class="summary-item">
              <span class="label">总问题数：</span>
              <span class="value">{{ currentNotice.total_issues_count }}</span>
            </div>
            <div class="summary-item">
              <span class="label">选中问题数：</span>
              <span class="value highlight">{{ selectedIssueIds.size }}</span>
            </div>
          </div>
        </el-alert>
      </div>

      <!-- 选中问题列表 -->
      <div class="selected-issues">
        <h4>选中的问题列表（共 {{ selectedIssues.length }} 个）</h4>
        <el-table :data="selectedIssues" stripe border max-height="600px">
          <!-- 序号 -->
          <el-table-column type="index" label="序号" width="60" />

          <!-- 基本信息 -->
          <el-table-column prop="section_name" label="标段" width="100" />
          <el-table-column prop="site_name" label="工点" width="100" />
          <el-table-column prop="description" label="问题描述" min-width="150" show-overflow-tooltip />

          <!-- 问题分类 -->
          <el-table-column prop="issue_category" label="问题类别" width="100" />
          <el-table-column prop="issue_type_level1" label="问题子类1" width="100" />
          <el-table-column prop="issue_type_level2" label="问题子类2" width="100" />

          <!-- 严重程度 -->
          <el-table-column prop="severity" label="严重程度" width="100">
            <template #default="{ row }">
              <el-tag :type="getSeverityType(row.severity)">
                {{ getSeverityLabel(row.severity) }}
              </el-tag>
            </template>
          </el-table-column>

          <!-- 通知类型 -->
          <el-table-column label="整改通知" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_rectification_notice ? 'success' : 'info'">
                {{ row.is_rectification_notice ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="不良行为" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_bad_behavior_notice ? 'warning' : 'info'">
                {{ row.is_bad_behavior_notice ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>

          <!-- 检查信息 -->
          <el-table-column prop="inspection_unit" label="检查单位" width="120" show-overflow-tooltip />
          <el-table-column prop="inspection_date" label="检查日期" width="100" />
          <el-table-column prop="inspection_personnel" label="检查人员" width="100" show-overflow-tooltip />

          <!-- 整改信息 -->
          <el-table-column prop="rectification_requirements" label="整改要求" min-width="150" show-overflow-tooltip />
          <el-table-column prop="rectification_deadline" label="整改期限" width="100" />

          <!-- 责任信息 -->
          <el-table-column prop="responsible_unit" label="责任单位" width="120" show-overflow-tooltip />
          <el-table-column prop="responsible_person" label="责任人" width="100" />
        </el-table>
      </div>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <el-button @click="handleBack">返回修改</el-button>
        <el-button @click="handleCancel">取消导入</el-button>
        <el-button type="primary" @click="handleConfirm" :loading="isLoading">
          确认导入
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useImportStore } from '@/stores/importStore'

const importStore = useImportStore()

const currentNotice = computed(() => {
  const notices = importStore.recognizedNotices
  if (notices.length > 0) {
    return notices[0]
  }
  return {}
})

const selectedIssueIds = computed(() => importStore.selectedIssueIds)

const selectedIssues = computed(() => {
  return importStore.recognizedIssues.filter((_, index) =>
    selectedIssueIds.value.has(index)
  )
})

const isLoading = computed(() => importStore.isLoading)

// 获取严重程度的标签
const getSeverityLabel = (severity) => {
  const labels = {
    1: '1 - 轻微',
    2: '2 - 一般',
    3: '3 - 中等',
    4: '4 - 严重',
    5: '5 - 极严重'
  }
  return labels[severity] || '未设置'
}

// 获取严重程度的标签类型
const getSeverityType = (severity) => {
  const types = {
    1: 'success',
    2: 'info',
    3: 'warning',
    4: 'danger',
    5: 'danger'
  }
  return types[severity] || 'info'
}

const handleBack = () => {
  importStore.viewMode = 'edit-issues'
}

const handleCancel = () => {
  importStore.resetRecognition()
}

const handleConfirm = async () => {
  const success = await importStore.importSelected()
  if (success) {
    // 导入成功，viewMode 已经改为 'result'
  }
}
</script>

<style scoped>
.import-confirm {
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

.summary {
  margin-bottom: 20px;
}

.summary-content {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  padding: 10px 0;
}

.summary-item {
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
  color: #f56c6c;
  font-weight: bold;
  font-size: 16px;
}

.selected-issues {
  margin-bottom: 20px;
}

.selected-issues h4 {
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

