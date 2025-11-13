<template>
  <div class="issues-page">
    <div class="issues-container">
      <h2 class="page-title">工程质量安全问题库</h2>

      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <div class="stat-content">
            <div class="stat-label">问题总数</div>
            <div class="stat-value">{{ totalIssues }}</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⚠️</div>
          <div class="stat-content">
            <div class="stat-label">质量问题</div>
            <div class="stat-value">{{ qualityIssues }}</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🚨</div>
          <div class="stat-content">
            <div class="stat-label">安全问题</div>
            <div class="stat-value">{{ safetyIssues }}</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📋</div>
          <div class="stat-content">
            <div class="stat-label">管理问题</div>
            <div class="stat-value">{{ managementIssues }}</div>
          </div>
        </div>
      </div>

      <!-- 问题表格 -->
      <div class="issues-section">
        <IssuesTable 
          :issues="issues"
          @row-click="handleIssueClick"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import IssuesTable from '../components/IssuesTable.vue'
import importService from '../services/importService'
import { ElMessage } from 'element-plus'
import { ISSUE_CATEGORIES } from '../config/issueCategories'

const router = useRouter()
const issues = ref([])
const isLoading = ref(false)

const totalIssues = computed(() => issues.value.length)
const qualityIssues = computed(() =>
  issues.value.filter(i => i.issue_category === ISSUE_CATEGORIES.QUALITY).length
)
const safetyIssues = computed(() =>
  issues.value.filter(i => i.issue_category === ISSUE_CATEGORIES.SAFETY).length
)
const managementIssues = computed(() =>
  issues.value.filter(i => i.issue_category === ISSUE_CATEGORIES.MANAGEMENT).length
)

const fetchIssues = async () => {
  isLoading.value = true
  try {
    console.log('🔍 IssuesPage: 开始获取问题列表...')
    const result = await importService.getIssues(1000, 0)
    console.log('✅ IssuesPage: 获取成功，result:', result)
    issues.value = Array.isArray(result) ? result : result.data || []
    console.log('✅ IssuesPage: issues.value:', issues.value)
  } catch (err) {
    console.error('❌ IssuesPage: 获取失败，错误:', err)
    ElMessage.error('获取问题列表失败')
    console.error(err)
  } finally {
    isLoading.value = false
  }
}

const handleIssueClick = (issue) => {
  router.push(`/issues/${issue.id}`)
}

onMounted(() => {
  fetchIssues()
})
</script>

<style scoped>
.issues-page {
  max-width: 1400px;
  margin: 0 auto;
}

.issues-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 32px;
}

.stat-content {
  flex: 1;
}

.stat-label {
  color: #999;
  font-size: 12px;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #667eea;
}

.issues-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>

