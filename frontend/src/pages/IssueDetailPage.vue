<template>
  <div class="issue-detail-page">
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
      <div v-else-if="issue" class="detail-content">
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
              <span class="value">{{ issue.check_date }}</span>
            </div>
            <div class="detail-item">
              <span class="label">检查单位</span>
              <span class="value">{{ issue.check_unit }}</span>
            </div>
            <div class="detail-item">
              <span class="label">项目名称</span>
              <span class="value">{{ issue.project_name }}</span>
            </div>
            <div class="detail-item">
              <span class="label">标段名称</span>
              <span class="value">{{ issue.section_name }}</span>
            </div>
            <div class="detail-item">
              <span class="label">工点名称</span>
              <span class="value">{{ issue.site_name }}</span>
            </div>
            <div class="detail-item">
              <span class="label">工点位置</span>
              <span class="value">{{ issue.site_location }}</span>
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
              <p class="value description">{{ issue.description }}</p>
            </div>
            <div class="detail-item">
              <span class="label">问题类型（一级）</span>
              <el-tag>{{ issue.issue_type_level1 }}</el-tag>
            </div>
            <div class="detail-item">
              <span class="label">问题类型（二级）</span>
              <span class="value">{{ issue.issue_type_level2 }}</span>
            </div>
            <div class="detail-item">
              <span class="label">严重程度</span>
              <el-tag :type="getSeverityType(issue.severity)">
                {{ issue.severity }}
              </el-tag>
            </div>
            <div class="detail-item">
              <span class="label">是否整改</span>
              <el-tag :type="issue.is_rectification ? 'success' : 'info'">
                {{ issue.is_rectification ? '已整改' : '未整改' }}
              </el-tag>
            </div>
          </div>
        </el-card>

        <!-- 检查依据卡片 -->
        <el-card v-if="issue.inspection_basis" class="detail-card">
          <template #header>
            <div class="card-header">
              <span>检查依据</span>
            </div>
          </template>

          <p class="value description">{{ issue.inspection_basis }}</p>
        </el-card>

        <!-- 整改信息卡片 -->
        <el-card v-if="issue.rectification_deadline || issue.rectification_description" class="detail-card">
          <template #header>
            <div class="card-header">
              <span>整改信息</span>
            </div>
          </template>

          <div class="detail-grid">
            <div class="detail-item">
              <span class="label">整改期限</span>
              <span class="value">{{ issue.rectification_deadline }}</span>
            </div>
            <div class="detail-item full-width">
              <span class="label">整改说明</span>
              <p class="value description">{{ issue.rectification_description }}</p>
            </div>
          </div>
        </el-card>

        <!-- 其他信息卡片 -->
        <el-card class="detail-card">
          <template #header>
            <div class="card-header">
              <span>其他信息</span>
            </div>
          </template>

          <div class="detail-grid">
            <div class="detail-item">
              <span class="label">责任单位</span>
              <span class="value">{{ issue.responsibility_unit }}</span>
            </div>
            <div class="detail-item">
              <span class="label">创建时间</span>
              <span class="value">{{ formatDate(issue.created_at) }}</span>
            </div>
            <div class="detail-item">
              <span class="label">更新时间</span>
              <span class="value">{{ formatDate(issue.updated_at) }}</span>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 错误状态 -->
      <el-empty v-else description="问题不存在或已删除" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import importService from '../services/importService'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

const issue = ref(null)
const isLoading = ref(false)

// 从路由参数获取 issueId
const issueId = computed(() => parseInt(route.params.id))

const getSeverityType = (severity) => {
  const typeMap = {
    '严重': 'danger',
    '一般': 'warning',
    '轻微': 'info'
  }
  return typeMap[severity] || 'info'
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const goBack = () => {
  console.log('🔴 IssueDetailPage: goBack 被调用')
  router.back()
}

const fetchIssueDetail = async () => {
  if (!issueId.value) {
    console.warn('⚠️ IssueDetailPage: issueId 无效')
    return
  }

  isLoading.value = true
  try {
    console.log('🔴 IssueDetailPage: 获取问题详情，issueId:', issueId.value)
    const result = await importService.getIssueDetail(issueId.value)
    console.log('✅ 获取成功:', result)
    issue.value = result
  } catch (err) {
    ElMessage.error('获取问题详情失败')
    console.error(err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  console.log('🔴 IssueDetailPage: onMounted，issueId:', issueId.value)
  fetchIssueDetail()
})

// 监听 issueId 变化
watch(() => issueId.value, () => {
  console.log('🔴 IssueDetailPage: issueId 变化，新值:', issueId.value)
  fetchIssueDetail()
})
</script>

<style scoped>
.issue-detail-page {
  max-width: 1000px;
  margin: 0 auto;
}

.detail-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card-header {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
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

.label {
  color: #999;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.value {
  color: #333;
  font-size: 14px;
  line-height: 1.5;
}

.description {
  white-space: pre-wrap;
  word-break: break-word;
  background-color: #f9f9f9;
  padding: 12px;
  border-radius: 4px;
  border-left: 3px solid #667eea;
}

@media (max-width: 768px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }

  .detail-item.full-width {
    grid-column: 1;
  }
}
</style>

