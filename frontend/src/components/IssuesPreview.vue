<template>
  <div class="issues-preview">
    <!-- 面包屑导航 -->
    <el-breadcrumb separator="/" style="margin-bottom: 20px">
      <el-breadcrumb-item @click="goBack" style="cursor: pointer">
        ← 返回
      </el-breadcrumb-item>
      <el-breadcrumb-item>问题列表</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 搜索和筛选 -->
    <div class="toolbar">
      <el-input
        v-model="searchText"
        placeholder="搜索项目名称、工点名称..."
        style="width: 300px"
        clearable
      />
      <el-select
        v-model="filterCategory"
        placeholder="问题类别"
        clearable
        style="width: 150px; margin-left: 12px"
      >
        <el-option label="工程质量" value="工程质量" />
        <el-option label="施工安全" value="施工安全" />
        <el-option label="管理行为" value="管理行为" />
        <el-option label="其它" value="其它" />
      </el-select>
      <el-button type="primary" @click="handleSearch" style="margin-left: 12px">
        搜索
      </el-button>
    </div>

    <!-- 统计信息 -->
    <div class="statistics" style="margin: 20px 0">
      <el-statistic title="总计" :value="totalCount" />
      <el-statistic title="工程质量" :value="qualityCount" />
      <el-statistic title="施工安全" :value="safetyCount" />
      <el-statistic title="管理行为" :value="managementCount" />
    </div>

    <!-- 表格 -->
    <el-table
      :data="paginatedIssues"
      stripe
      style="width: 100%; margin-top: 16px"
      highlight-current-row
    >
      <!-- 序号 -->
      <el-table-column type="index" label="序号" width="60" />

      <!-- 检查时间 -->
      <el-table-column prop="inspection_date" label="检查时间" width="120" />

      <!-- 检查单位 -->
      <el-table-column prop="inspection_unit" label="检查单位" width="120" />

      <!-- 项目名称 -->
      <el-table-column prop="project_name" label="项目名称" width="120" />

      <!-- 标段 -->
      <el-table-column prop="section_name" label="标段" width="120" />

      <!-- 工点名称 -->
      <el-table-column prop="site_name" label="工点名称" width="120" />

      <!-- 问题类别 -->
      <el-table-column prop="issue_category" label="问题类别" width="120">
        <template #default="{ row }">
          <el-tag>{{ row.issue_category || row.issue_type_level1 || '-' }}</el-tag>
        </template>
      </el-table-column>

      <!-- 问题类型 -->
      <el-table-column prop="issue_type_level2" label="问题类型" width="120" />

      <!-- 描述 -->
      <el-table-column prop="description" label="描述" width="200">
        <template #default="{ row }">
          <el-tooltip :content="row.description" placement="top">
            <span>{{ truncateText(row.description, 30) }}</span>
          </el-tooltip>
        </template>
      </el-table-column>

      <!-- 严重程度 -->
      <el-table-column prop="severity" label="严重程度" width="100">
        <template #default="{ row }">
          <el-tag :type="getSeverityType(row.severity)">
            {{ row.severity || '-' }}
          </el-tag>
        </template>
      </el-table-column>

      <!-- 操作 -->
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="handleSelectIssue(row)">
            详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="totalCount"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="handlePageChange"
      />
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

const searchText = ref('')
const filterCategory = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

// 获取问题列表
const issues = computed(() => {
  // 优先使用 importStore 中的问题列表
  if (importStore.noticeIssues && importStore.noticeIssues.length > 0) {
    return importStore.noticeIssues
  }
  // 其次使用 noticeStore 中的问题列表
  if (noticeStore.noticeIssues && noticeStore.noticeIssues.length > 0) {
    return noticeStore.noticeIssues
  }
  return []
})

// 过滤后的问题列表
const filteredIssues = computed(() => {
  let filtered = issues.value

  // 按搜索文本过滤
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(issue =>
      (issue.project_name && issue.project_name.toLowerCase().includes(search)) ||
      (issue.site_name && issue.site_name.toLowerCase().includes(search))
    )
  }

  // 按类别过滤
  if (filterCategory.value) {
    filtered = filtered.filter(issue =>
      (issue.issue_category === filterCategory.value) ||
      (issue.issue_type_level1 === filterCategory.value)
    )
  }

  return filtered
})

// 分页后的问题列表
const paginatedIssues = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredIssues.value.slice(start, end)
})

// 统计信息
const totalCount = computed(() => issues.value.length)
const qualityCount = computed(() =>
  issues.value.filter(i => (i.issue_category || i.issue_type_level1) === '工程质量').length
)
const safetyCount = computed(() =>
  issues.value.filter(i => (i.issue_category || i.issue_type_level1) === '施工安全').length
)
const managementCount = computed(() =>
  issues.value.filter(i => (i.issue_category || i.issue_type_level1) === '管理行为').length
)

// 截断文本
const truncateText = (text, length) => {
  if (!text) return '-'
  return text.length > length ? text.substring(0, length) + '...' : text
}

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

// 搜索
const handleSearch = () => {
  currentPage.value = 1
}

// 分页变化
const handlePageChange = () => {
  // 分页自动更新
}

// 选择问题
const handleSelectIssue = (issue) => {
  // 设置选中的问题
  importStore.selectedIssueId = issue.id || issue.issue_id
  noticeStore.selectedIssue = issue

  // 更新视图模式
  if (importStore.viewMode === 'issues') {
    importStore.viewMode = 'detail'
  } else if (noticeStore.viewMode === 'issues') {
    noticeStore.viewMode = 'issue-detail'
  }
}

// 返回
const goBack = () => {
  if (importStore.viewMode === 'issues') {
    importStore.viewMode = 'notices'
  } else if (noticeStore.viewMode === 'issues') {
    noticeStore.viewMode = 'list'
  } else {
    router.back()
  }
}

onMounted(() => {
  // 初始化
})
</script>

<style scoped>
.issues-preview {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  align-items: center;
}

.statistics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding: 20px 0;
}

:deep(.el-table) {
  background-color: white;
}

:deep(.el-tag) {
  margin-right: 8px;
}
</style>
