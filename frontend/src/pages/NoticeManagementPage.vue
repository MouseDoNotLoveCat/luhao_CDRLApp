<template>
  <div class="notice-management-page">
    <!-- 列表视图 -->
    <div v-if="noticeStore.viewMode === 'list'">
      <NoticesListComponent @view-detail="handleViewNoticeDetail" />
    </div>

    <!-- 问题详情视图（复用导入预览的 IssueDetailPreview） -->
    <!-- 注意：这个条件必须在问题列表视图之前，因为两者都使用 importStore -->
    <div v-else-if="importStore.viewMode === 'detail'">
      <IssueDetailPreview />
    </div>

    <!-- 问题列表视图（复用导入预览的 IssuesPreview） -->
    <div v-else-if="noticeStore.viewMode === 'detail'">
      <IssuesPreview />
    </div>
  </div>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { useNoticeManagementStore } from '../stores/noticeManagementStore'
import { useImportStore } from '../stores/importStore'
import NoticesListComponent from '../components/NoticesListComponent.vue'
import IssuesPreview from '../components/IssuesPreview.vue'
import IssueDetailPreview from '../components/IssueDetailPreview.vue'

const noticeStore = useNoticeManagementStore()
const importStore = useImportStore()

// 调试：监听 viewMode 变化
watch(() => importStore.viewMode, (newVal) => {
  console.log('🔍 importStore.viewMode changed to:', newVal)
})

watch(() => noticeStore.viewMode, (newVal) => {
  console.log('🔍 noticeStore.viewMode changed to:', newVal)
})

onMounted(() => {
  // 初始化加载通知书列表
  noticeStore.fetchNotices()
})

const handleViewNoticeDetail = async (notice) => {
  console.log('🔍 handleViewNoticeDetail called with notice:', notice)
  // 加载通知书详情（会自动同步到 importStore）
  await noticeStore.fetchNoticeDetail(notice.id)
  console.log('   After fetchNoticeDetail, noticeStore.noticeIssues:', noticeStore.noticeIssues)
  console.log('   importStore.noticeIssues:', importStore.noticeIssues)

  // 切换到问题列表视图
  noticeStore.viewMode = 'detail'
}
</script>

<style scoped>
.notice-management-page {
  padding: 20px;
}
</style>

