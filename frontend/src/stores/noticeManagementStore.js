import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'
import { useImportStore } from './importStore'

export const useNoticeManagementStore = defineStore('noticeManagement', () => {
  // 状态
  const notices = ref([])
  const noticesTotal = ref(0)
  const noticesPage = ref(1)
  const noticesPageSize = ref(20)
  const noticesSearch = ref('')
  const isLoading = ref(false)
  const error = ref(null)
  
  // 选中的通知书
  const selectedNoticeId = ref(null)
  const selectedNotice = ref(null)
  const noticeIssues = ref([])
  const selectedIssue = ref(null)  // 选中的问题

  // 视图模式
  const viewMode = ref('list')  // 'list' | 'detail' | 'issues' | 'issue-detail'
  
  // 获取通知书列表
  const fetchNotices = async () => {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.get('/notices', {
        params: {
          search: noticesSearch.value,
          limit: noticesPageSize.value,
          offset: (noticesPage.value - 1) * noticesPageSize.value
        }
      })
      console.log('Notices API Response:', response)
      notices.value = response.data
      noticesTotal.value = response.total
    } catch (err) {
      error.value = err.response?.data?.detail || '获取通知书列表失败'
      console.error('获取通知书列表失败:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  // 获取通知书详情
  const fetchNoticeDetail = async (noticeId) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.get(`/notices/${noticeId}`)
      console.log('Notice Detail Response:', response)
      selectedNotice.value = response
      noticeIssues.value = response.issues || []
      selectedNoticeId.value = noticeId
      viewMode.value = 'detail'

      // 同步数据到 importStore 以复用导入预览的组件
      const importStore = useImportStore()
      console.log('🔍 Syncing to importStore...')
      console.log('   noticeIssues:', noticeIssues.value)
      importStore.noticeIssues = noticeIssues.value
      importStore.selectedNoticeId = noticeId
      importStore.importedNotices = [response]
      console.log('   After sync, importStore.noticeIssues:', importStore.noticeIssues)
    } catch (err) {
      error.value = err.response?.data?.detail || '获取通知书详情失败'
      console.error('获取通知书详情失败:', err)
    } finally {
      isLoading.value = false
    }
  }
  
  // 删除通知书
  const deleteNotice = async (noticeId) => {
    try {
      const response = await api.delete(`/notices/${noticeId}`)
      console.log('Delete Notice Response:', response)
      
      // 从列表中移除
      notices.value = notices.value.filter(n => n.id !== noticeId)
      noticesTotal.value -= 1
      
      return {
        success: true,
        message: response.message || '通知书已删除'
      }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || '删除通知书失败'
      error.value = errorMsg
      console.error('删除通知书失败:', err)
      return {
        success: false,
        message: errorMsg
      }
    }
  }
  
  // 搜索
  const handleSearch = () => {
    noticesPage.value = 1
    fetchNotices()
  }
  
  // 返回列表
  const goBackToList = () => {
    selectedNoticeId.value = null
    selectedNotice.value = null
    noticeIssues.value = []
    viewMode.value = 'list'
  }
  
  // 选择通知书
  const selectNotice = (notice) => {
    fetchNoticeDetail(notice.id)
  }
  
  return {
    // 状态
    notices,
    noticesTotal,
    noticesPage,
    noticesPageSize,
    noticesSearch,
    isLoading,
    error,
    selectedNoticeId,
    selectedNotice,
    noticeIssues,
    selectedIssue,
    viewMode,

    // 方法
    fetchNotices,
    fetchNoticeDetail,
    deleteNotice,
    handleSearch,
    goBackToList,
    selectNotice
  }
})

