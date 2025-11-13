<template>
  <div class="issue-detail-preview">
    <div class="detail-container">
      <!-- 返回按钮 -->
      <div class="header-actions">
        <el-button type="primary" link @click="goBack">
          ← 返回列表
        </el-button>
      </div>

      <!-- 加载状态 -->
      <el-skeleton v-if="isLoading" :rows="10" animated />

      <!-- 问题详情 -->
      <div v-else-if="currentIssue" class="detail-content">
        <!-- 基本信息卡片 -->
        <el-card class="detail-card">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
            </div>
          </template>

          <div class="detail-grid">
            <div class="detail-item">
              <span class="label">检查日期</span>
              <span class="value">{{ currentIssue.check_date || currentIssue.inspection_date || '-' }}</span>
            </div>
            <div class="detail-item">
              <span class="label">检查单位</span>
              <span class="value">{{ currentIssue.check_unit || currentIssue.inspection_unit || '-' }}</span>
            </div>
            <div class="detail-item">
              <span class="label">项目名称</span>
              <span class="value">{{ currentIssue.project_name || '-' }}</span>
            </div>
            <div class="detail-item">
              <span class="label">标段名称</span>
              <span class="value">{{ currentIssue.section_name || '-' }}</span>
            </div>
            <div class="detail-item">
              <span class="label">工点名称</span>
              <span class="value">{{ currentIssue.site_name || '-' }}</span>
            </div>
            <div class="detail-item">
              <span class="label">工点位置</span>
              <span class="value">{{ currentIssue.site_location || '-' }}</span>
            </div>
          </div>
        </el-card>

        <!-- 问题信息卡片 -->
        <el-card class="detail-card">
          <template #header>
            <div class="card-header">
              <span>问题信息</span>
            </div>
          </template>

          <div class="detail-grid">
            <div class="detail-item full-width">
              <span class="label">问题描述</span>
              <p class="value description">{{ currentIssue.description || '-' }}</p>
            </div>
            <div class="detail-item">
              <span class="label">问题类别</span>
              <el-tag>{{ currentIssue.issue_category || currentIssue.issue_type_level1 || '-' }}</el-tag>
            </div>
            <div class="detail-item">
              <span class="label">问题类型（二级）</span>
              <span class="value">{{ currentIssue.issue_type_level2 || '-' }}</span>
            </div>
            <div class="detail-item">
              <span class="label">严重程度</span>
              <el-tag :type="getSeverityType(currentIssue.severity)">
                {{ currentIssue.severity || '-' }}
              </el-tag>
            </div>
            <div class="detail-item">
              <span class="label">是否整改</span>
              <el-tag :type="currentIssue.is_rectification ? 'success' : 'info'">
                {{ currentIssue.is_rectification ? '已整改' : '未整改' }}
              </el-tag>
            </div>
          </div>
        </el-card>

        <!-- 检查依据卡片 -->
        <el-card v-if="currentIssue.inspection_basis" class="detail-card">
          <template #header>
            <div class="card-header">
              <span>检查依据</span>
            </div>
          </template>

          <p class="value description">{{ currentIssue.inspection_basis }}</p>
        </el-card>

        <!-- 整改信息卡片 -->
        <el-card v-if="currentIssue.rectification_deadline || currentIssue.rectification_description" class="detail-card">
          <template #header>
            <div class="card-header">
              <span>整改信息</span>
            </div>
          </template>

          <div class="detail-grid">
            <div class="detail-item" v-if="currentIssue.rectification_deadline">
              <span class="label">整改期限</span>
              <span class="value">{{ currentIssue.rectification_deadline }}</span>
            </div>
            <div class="detail-item full-width" v-if="currentIssue.rectification_description">
              <span class="label">整改说明</span>
              <p class="value description">{{ currentIssue.rectification_description }}</p>
            </div>
          </div>
        </el-card>

        <!-- 责任人信息卡片 -->
        <el-card v-if="currentIssue.responsible_person || currentIssue.rectification_unit" class="detail-card">
          <template #header>
            <div class="card-header">
              <span>责任人信息</span>
            </div>
          </template>

          <div class="detail-grid">
            <div class="detail-item" v-if="currentIssue.responsible_person">
              <span class="label">责任人</span>
              <span class="value">{{ currentIssue.responsible_person }}</span>
            </div>
            <div class="detail-item" v-if="currentIssue.rectification_unit">
              <span class="label">整改单位</span>
              <span class="value">{{ currentIssue.rectification_unit }}</span>
            </div>
            <div class="detail-item" v-if="currentIssue.rectification_person">
              <span class="label">整改人</span>
              <span class="value">{{ currentIssue.rectification_person }}</span>
            </div>
            <div class="detail-item" v-if="currentIssue.sign_off_person">
              <span class="label">签字人</span>
              <span class="value">{{ currentIssue.sign_off_person }}</span>
            </div>
            <div class="detail-item" v-if="currentIssue.sign_off_status">
              <span class="label">签字状态</span>
              <el-tag>{{ currentIssue.sign_off_status }}</el-tag>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 无数据提示 -->
      <el-empty v-else description="未找到问题详情" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useImportStore } from '../stores/importStore'
import { useNoticeManagementStore } from '../stores/noticeManagementStore'

const router = useRouter()
const importStore = useImportStore()
const noticeStore = useNoticeManagementStore()

const isLoading = ref(false)

// 获取当前问题
const currentIssue = computed(() => {
  // 首先尝试从 importStore 获取
  if (importStore.selectedIssueId && importStore.noticeIssues) {
    const issue = importStore.noticeIssues.find(
      i => i.id === importStore.selectedIssueId || i.issue_id === importStore.selectedIssueId
    )
    if (issue) return issue
  }

  // 其次尝试从 noticeStore 获取
  if (noticeStore.selectedIssue) {
    return noticeStore.selectedIssue
  }

  return null
})

// 获取严重程度的标签类型
const getSeverityType = (severity) => {
  const typeMap = {
    '严重': 'danger',
    '一般': 'warning',
    '轻微': 'info',
    '较重': 'danger',
    '特别严重': 'danger'
  }
  return typeMap[severity] || 'info'
}

// 返回列表
const goBack = () => {
  // 检查是否来自导入页面
  if (importStore.viewMode === 'detail') {
    importStore.viewMode = 'issues'
  }
  // 检查是否来自通知书管理页面
  else if (noticeStore.viewMode === 'issue-detail') {
    noticeStore.viewMode = 'issues'
  }
  // 否则返回上一页
  else {
    router.back()
  }
}

onMounted(() => {
  isLoading.value = false
})
</script>

<style scoped>
.issue-detail-preview {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.detail-container {
  max-width: 1200px;
  margin: 0 auto;
}

.header-actions {
  margin-bottom: 20px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-card {
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-item .label {
  font-weight: 600;
  color: #666;
  font-size: 14px;
}

.detail-item .value {
  color: #333;
  font-size: 14px;
  word-break: break-word;
}

.detail-item .description {
  white-space: pre-wrap;
  line-height: 1.6;
  margin: 0;
}

:deep(.el-tag) {
  margin-right: 8px;
}
</style>
