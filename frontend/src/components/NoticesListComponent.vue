<template>
  <div class="notices-list-container">
    <!-- 标题和操作栏 -->
    <div class="list-header">
      <h2>通知书一览表</h2>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="store.noticesSearch"
        placeholder="搜索通知书编号或项目名称..."
        clearable
        @input="handleSearch"
      >
        <template #suffix>
          <el-icon class="is-loading" v-if="store.isLoading">
            <Loading />
          </el-icon>
        </template>
      </el-input>
    </div>

    <!-- 错误提示 -->
    <el-alert
      v-if="store.error"
      :title="store.error"
      type="error"
      closable
      @close="store.error = null"
      class="error-alert"
    />

    <!-- 通知书表格 -->
    <el-table
      :data="displayNotices"
      stripe
      style="width: 100%"
      :default-sort="{ prop: 'id', order: 'descending' }"
    >
      <el-table-column prop="notice_number" label="通知书编号" min-width="150" />
      <el-table-column prop="check_date" label="检查日期" width="120" />
      <el-table-column prop="check_unit" label="检查单位" min-width="150" />
      <el-table-column prop="issues_count" label="问题数量" width="100" align="center" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="200" align="center">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-button
              type="primary"
              size="small"
              @click.stop="handleViewDetail(row)"
            >
              查看详情
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click.stop="handleDeleteNotice(row)"
            >
              删除
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="store.noticesPage"
        v-model:page-size="store.noticesPageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="store.noticesTotal"
        layout="total, sizes, prev, pager, next, jumper"
        @change="store.fetchNotices"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useNoticeManagementStore } from '../stores/noticeManagementStore'
import { useImportStore } from '../stores/importStore'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'

const store = useNoticeManagementStore()
const importStore = useImportStore()

const emit = defineEmits(['view-detail'])

// 判断是否显示导入的通知书列表
const isShowingImportedNotices = computed(() => {
  return importStore.importedNotices.length > 0
})

// 获取要显示的通知书列表
const displayNotices = computed(() => {
  if (isShowingImportedNotices.value) {
    return importStore.importedNotices
  }
  return store.notices
})

const handleSearch = () => {
  store.noticesPage = 1
  store.fetchNotices()
}

const handleViewDetail = (row) => {
  // 如果是显示导入的通知书，使用 importStore
  if (isShowingImportedNotices.value) {
    importStore.selectNotice(row.id)
  } else {
    // 否则使用 noticeManagementStore
    store.selectNotice(row)
  }
}

const handleDeleteNotice = (row) => {
  ElMessageBox.confirm(
    `确定要删除通知书"${row.notice_number}"吗？该操作将同时删除所有关联的问题。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    const result = await store.deleteNotice(row.id)
    if (result.success) {
      ElMessage.success('通知书已删除')
    } else {
      ElMessage.error(result.message)
    }
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}
</script>

<style scoped>
.notices-list-container {
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.list-header h2 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.search-bar {
  margin-bottom: 20px;
}

.error-alert {
  margin-bottom: 20px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

:deep(.el-table__row) {
  cursor: pointer;
  transition: background-color 0.3s;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
}

.action-buttons :deep(.el-button) {
  margin: 0;
}
</style>

