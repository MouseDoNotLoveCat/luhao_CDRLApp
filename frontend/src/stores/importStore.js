import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import importService from '../services/importService'

export const useImportStore = defineStore('import', () => {
  // 状态
  const selectedFile = ref(null)
  const selectedFiles = ref([])  // 批量导入的文件列表
  const isLoading = ref(false)
  const isBatchLoading = ref(false)  // 批量导入加载状态
  const importResult = ref(null)
  const batchImportResult = ref(null)  // 批量导入结果
  const error = ref(null)
  const issues = ref([])
  const currentPage = ref(1)
  const pageSize = ref(20)
  const totalIssues = ref(0)
  const batchProgress = ref(0)  // 批量导入进度 (0-100)

  // 三层导航状态
  const viewMode = ref('upload')  // 'upload' | 'recognizing' | 'preview-notices' | 'preview-issues' | 'confirm' | 'importing' | 'result' | 'notices' | 'issues' | 'detail'
  const importedNotices = ref([])  // 已导入的通知书列表
  const selectedNoticeId = ref(null)  // 当前选中的通知书 ID
  const selectedIssueId = ref(null)  // 当前选中的问题 ID
  const noticeIssues = ref([])  // 当前通知书的问题列表

  // 新增：识别和缓存状态
  const recognizedNotices = ref([])  // 识别的通知书列表
  const recognizedIssues = ref([])  // 识别的问题列表
  const currentRecognizedNoticeId = ref(null)  // 当前预览的通知书 ID

  // 新增：用户选择状态
  const selectedNoticeIds = ref(new Set())  // 选中的通知书 ID
  const selectedIssueIds = ref(new Set())  // 选中的问题 ID

  // 新增：编辑和验证状态
  const editedData = ref({})  // 编辑的数据
  const validationErrors = ref({})  // 验证错误
  const modifiedRecords = ref(new Set())  // 已修改的记录

  // 新增：导入流程状态
  const importStep = ref(1)  // 导入步骤
  const importProgress = ref(0)  // 导入进度 (0-100)

  // 新增：项目-标段映射状态
  const sectionProjectMapping = ref({})  // { section_name: { project_id, project_name, builder_unit } }

  // 计算属性
  const hasFile = computed(() => selectedFile.value !== null)
  const fileName = computed(() => selectedFile.value?.name || '')
  const fileSize = computed(() => {
    if (!selectedFile.value) return ''
    const size = selectedFile.value.size
    if (size < 1024) return `${size} B`
    if (size < 1024 * 1024) return `${(size / 1024).toFixed(2)} KB`
    return `${(size / (1024 * 1024)).toFixed(2)} MB`
  })

  // 批量导入相关计算属性
  const hasFiles = computed(() => selectedFiles.value.length > 0)
  const filesCount = computed(() => selectedFiles.value.length)
  const totalFilesSize = computed(() => {
    const total = selectedFiles.value.reduce((sum, file) => sum + file.size, 0)
    if (total < 1024) return `${total} B`
    if (total < 1024 * 1024) return `${(total / 1024).toFixed(2)} KB`
    return `${(total / (1024 * 1024)).toFixed(2)} MB`
  })

  // 方法
  const setSelectedFile = (file) => {
    selectedFile.value = file
    error.value = null
  }

  const clearSelectedFile = () => {
    selectedFile.value = null
    importResult.value = null
    error.value = null
  }

  const importDocument = async () => {
    if (!selectedFile.value) {
      error.value = '请先选择文件'
      return false
    }

    isLoading.value = true
    error.value = null

    try {
      const result = await importService.importDocument(selectedFile.value)
      importResult.value = result

      // 为每个问题添加检查日期和检查单位
      const enrichedIssues = (result.issues || []).map(issue => ({
        ...issue,
        check_date: result.check_date,
        check_unit: result.check_unit,
        project_name: result.project_name
      }))

      issues.value = enrichedIssues
      totalIssues.value = result.total_issues_count || 0
      return true
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || '导入失败'
      return false
    } finally {
      isLoading.value = false
    }
  }

  const fetchIssues = async (page = 1) => {
    currentPage.value = page
    const offset = (page - 1) * pageSize.value
    
    try {
      const result = await importService.getIssues(pageSize.value, offset)
      issues.value = result
      return result
    } catch (err) {
      error.value = err.message || '获取问题列表失败'
      return []
    }
  }

  const resetImport = () => {
    selectedFile.value = null
    importResult.value = null
    error.value = null
    issues.value = []
    currentPage.value = 1
  }

  // 批量导入相关方法
  const setSelectedFiles = (files) => {
    selectedFiles.value = Array.from(files)
    error.value = null
  }

  const addSelectedFiles = (files) => {
    selectedFiles.value = [...selectedFiles.value, ...Array.from(files)]
    error.value = null
  }

  const removeSelectedFile = (index) => {
    selectedFiles.value.splice(index, 1)
  }

  const clearSelectedFiles = () => {
    selectedFiles.value = []
    batchImportResult.value = null
    error.value = null
    batchProgress.value = 0
  }

  const importBatch = async () => {
    if (selectedFiles.value.length === 0) {
      error.value = '请先选择至少一个文件'
      return false
    }

    isBatchLoading.value = true
    error.value = null
    batchProgress.value = 0

    try {
      const result = await importService.importBatch(selectedFiles.value)
      batchImportResult.value = result
      batchProgress.value = 100

      // 将成功导入的通知书添加到 importedNotices 数组
      if (result.details && Array.isArray(result.details)) {
        result.details.forEach(detail => {
          // 跳过重复的通知书
          if (detail.duplicate) {
            console.warn(`通知书 ${detail.notice_number} 已存在，跳过导入`)
            return
          }

          if (detail.success) {
            // 为每个问题添加检查日期和检查单位
            const enrichedIssues = (detail.issues || []).map(issue => ({
              ...issue,
              check_date: detail.check_date,
              check_unit: detail.check_unit,
              project_name: detail.project_name
            }))

            // 创建通知书对象
            const notice = {
              id: detail.id || `batch_${Date.now()}_${Math.random()}`,
              notice_number: detail.notice_number,
              project_name: detail.project_name,
              check_date: detail.check_date,
              check_unit: detail.check_unit,
              issues_count: detail.total_issues || 0,
              issues: enrichedIssues
            }
            importedNotices.value.push(notice)
          }
        })
      }

      return true
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || '批量导入失败'
      return false
    } finally {
      isBatchLoading.value = false
    }
  }

  const resetBatchImport = () => {
    selectedFiles.value = []
    batchImportResult.value = null
    error.value = null
    batchProgress.value = 0
  }

  // 统一导入方法 - 根据文件数量自动选择单文件或批量导入
  const importFiles = async () => {
    if (selectedFiles.value.length === 0) {
      error.value = '请先选择至少一个文件'
      return false
    }

    // 如果只有一个文件，使用单文件导入
    if (selectedFiles.value.length === 1) {
      return await importSingleFile()
    }

    // 多个文件，使用批量导入
    return await importBatch()
  }

  // 单文件导入（从 selectedFiles 中获取）
  const importSingleFile = async () => {
    if (selectedFiles.value.length === 0) {
      error.value = '请先选择文件'
      return false
    }

    isLoading.value = true
    error.value = null

    try {
      const file = selectedFiles.value[0]
      const result = await importService.importDocument(file)
      importResult.value = result

      // 检查是否重复
      if (result.duplicate) {
        error.value = result.error
        return false
      }

      // 检查是否导入失败
      if (!result.success) {
        error.value = result.error
        return false
      }

      // 为每个问题添加检查日期和检查单位
      const enrichedIssues = (result.issues || []).map(issue => ({
        ...issue,
        check_date: result.check_date,
        check_unit: result.check_unit,
        project_name: result.project_name
      }))

      issues.value = enrichedIssues
      totalIssues.value = result.total_issues_count || 0

      // 添加到已导入的通知书列表
      const notice = {
        id: result.id || Date.now(),
        notice_number: result.notice_number,
        project_name: result.project_name,
        check_date: result.check_date,
        check_unit: result.check_unit,
        issues_count: result.total_issues_count || 0,
        issues: enrichedIssues
      }
      importedNotices.value.push(notice)

      return true
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || '导入失败'
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 三层导航方法
  const goToNoticesList = () => {
    viewMode.value = 'notices'
    selectedNoticeId.value = null
    selectedIssueId.value = null
  }

  const selectNotice = (noticeId) => {
    selectedNoticeId.value = noticeId
    const notice = importedNotices.value.find(n => n.id === noticeId)
    if (notice) {
      noticeIssues.value = notice.issues || []
    }
    viewMode.value = 'issues'
  }

  const selectIssue = (issueId) => {
    console.log('🔍 selectIssue called with issueId:', issueId)
    console.log('   Current noticeIssues:', noticeIssues.value)
    selectedIssueId.value = issueId
    viewMode.value = 'detail'
    console.log('   After selectIssue, viewMode:', viewMode.value)
    console.log('   selectedIssueId:', selectedIssueId.value)
  }

  const goBackToNotices = () => {
    selectedIssueId.value = null
    viewMode.value = 'issues'
  }

  const goBackToUpload = () => {
    viewMode.value = 'upload'
    selectedNoticeId.value = null
    selectedIssueId.value = null
    importedNotices.value = []
    noticeIssues.value = []
    // 清空已选择的文件
    selectedFiles.value = []
    importResult.value = null
    batchImportResult.value = null
    error.value = null
    issues.value = []
    batchProgress.value = 0
    // 清空识别状态
    recognizedNotices.value = []
    recognizedIssues.value = []
    currentRecognizedNoticeId.value = null
    selectedNoticeIds.value = new Set()
    selectedIssueIds.value = new Set()
    editedData.value = {}
    validationErrors.value = {}
    modifiedRecords.value = new Set()
    importStep.value = 1
    importProgress.value = 0
  }

  // 新增：识别文档
  const recognizeDocument = async () => {
    if (selectedFiles.value.length === 0) {
      error.value = '请先选择文件'
      console.error('❌ 识别失败: 未选择文件')
      return false
    }

    isLoading.value = true
    error.value = null
    viewMode.value = 'recognizing'

    try {
      const file = selectedFiles.value[0]
      console.log('🔄 开始识别文件:', file.name, '大小:', file.size)

      const result = await importService.recognizeDocument(file)

      console.log('📦 收到识别结果:', result)

      if (!result || !result.success) {
        const errorMsg = result?.error || '识别失败，未收到有效响应'
        error.value = errorMsg
        console.error('❌ 识别失败:', errorMsg)
        viewMode.value = 'upload'
        return false
      }

      console.log('✅ 识别成功，问题数:', result.issues?.length || 0)

      // 缓存识别结果
      recognizedNotices.value = [result]
      recognizedIssues.value = result.issues || []
      currentRecognizedNoticeId.value = 0

      // 转到预览通知书界面
      viewMode.value = 'preview-notices'
      return true
    } catch (err) {
      // 检查是否是超时错误
      let errorMsg = err.message || '识别失败'

      if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
        errorMsg = '识别超时：文件处理耗时过长，请稍候或尝试使用较小的文件'
        console.error('⏱️  识别超时：请求在 5 分钟后仍未完成')
      }

      error.value = errorMsg
      console.error('❌ 识别异常:', err)
      console.error('   错误详情:', err.response?.data || err)
      viewMode.value = 'upload'
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 新增：预览通知书
  const previewNotices = () => {
    viewMode.value = 'preview-notices'
  }

  // 新增：预览问题
  const previewIssues = () => {
    viewMode.value = 'preview-issues'
  }

  // 新增：切换通知书选择
  const toggleNoticeSelection = (noticeId) => {
    if (selectedNoticeIds.value.has(noticeId)) {
      selectedNoticeIds.value.delete(noticeId)
    } else {
      selectedNoticeIds.value.add(noticeId)
    }
  }

  // 新增：切换问题选择
  const toggleIssueSelection = (issueId) => {
    if (selectedIssueIds.value.has(issueId)) {
      selectedIssueIds.value.delete(issueId)
    } else {
      selectedIssueIds.value.add(issueId)
    }
  }

  // 新增：编辑记录
  const editRecord = (recordId, fieldName, value) => {
    if (!editedData.value[recordId]) {
      editedData.value[recordId] = {}
    }
    editedData.value[recordId][fieldName] = value
    modifiedRecords.value.add(recordId)
  }

  // 新增：更新识别的问题（行内编辑）
  const updateRecognizedIssue = (issueIndex, fieldName, value) => {
    if (issueIndex >= 0 && issueIndex < recognizedIssues.value.length) {
      recognizedIssues.value[issueIndex][fieldName] = value
      modifiedRecords.value.add(`issue_${issueIndex}`)
    }
  }

  // 新增：更新标段的项目关联
  const updateSectionProject = (sectionName, projectInfo) => {
    sectionProjectMapping.value[sectionName] = projectInfo
  }

  // 新增：批量初始化标段-项目映射（从识别结果中提取）
  const initializeSectionProjectMapping = () => {
    const mapping = {}
    const projectName = recognizedNotices.value[0]?.project_name || '未知项目'

    // 遍历所有识别的问题，提取唯一的标段名称
    recognizedIssues.value.forEach(issue => {
      const sectionName = issue.section_name
      if (sectionName && !mapping[sectionName]) {
        mapping[sectionName] = {
          project_id: null,  // 初始为 null，需要用户确认
          project_name: projectName,
          builder_unit: recognizedNotices.value[0]?.builder_unit || ''
        }
      }
    })

    sectionProjectMapping.value = mapping
  }

  // 新增：根据项目名称获取标段列表
  const fetchSectionsByProject = async (projectName) => {
    try {
      if (!projectName) return []
      const response = await fetch(`/api/sections?project_name=${encodeURIComponent(projectName)}`)
      if (!response.ok) {
        console.error('Failed to fetch sections:', response.statusText)
        return []
      }
      const data = await response.json()
      return data || []
    } catch (error) {
      console.error('Error fetching sections:', error)
      return []
    }
  }

  // 新增：验证记录
  const validateRecord = (recordId) => {
    // 这里可以添加具体的验证逻辑
    if (validationErrors.value[recordId]) {
      delete validationErrors.value[recordId]
    }
  }

  // 新增：验证所有记录
  const validateAllRecords = () => {
    validationErrors.value = {}
    // 这里可以添加批量验证逻辑
    return Object.keys(validationErrors.value).length === 0
  }

  // 新增：导入选中的记录
  const importSelected = async () => {
    if (selectedIssueIds.value.size === 0) {
      error.value = '请先选择至少一个问题'
      return false
    }

    viewMode.value = 'importing'
    isLoading.value = true
    error.value = null
    importProgress.value = 0

    try {
      const noticeData = recognizedNotices.value[0]

      // 构建选中的完整问题数据（包括用户编辑的字段）
      const selectedIssues = recognizedIssues.value.filter((_, index) =>
        selectedIssueIds.value.has(index)
      )

      // 更新 noticeData 中的 issues 为选中的问题
      const updatedNoticeData = {
        ...noticeData,
        issues: selectedIssues,
        sectionProjectMapping: sectionProjectMapping.value  // 添加项目-标段映射
      }

      const result = await importService.importSelected(updatedNoticeData, Array.from(selectedIssueIds.value))

      if (!result.success) {
        error.value = result.error
        importResult.value = result // 将失败结果也存入 importResult
        viewMode.value = 'result' // 统一导航到结果页
        return false
      }

      importProgress.value = 100
      viewMode.value = 'result'
      importResult.value = result
      return true
    } catch (err) {
      error.value = err.message || '导入失败'
      // 将错误信息包装成与成功结果类似的结构
      importResult.value = {
        success: false,
        error: error.value
      }
      viewMode.value = 'result' // 统一导航到结果页
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 新增：重置识别状态
  const resetRecognition = () => {
    recognizedNotices.value = []
    recognizedIssues.value = []
    currentRecognizedNoticeId.value = null
    selectedNoticeIds.value = new Set()
    selectedIssueIds.value = new Set()
    editedData.value = {}
    validationErrors.value = {}
    modifiedRecords.value = new Set()
    importStep.value = 1
    importProgress.value = 0
    sectionProjectMapping.value = {}  // 重置项目-标段映射
    viewMode.value = 'upload'
  }

  return {
    // 状态
    selectedFile,
    selectedFiles,
    isLoading,
    isBatchLoading,
    importResult,
    batchImportResult,
    error,
    issues,
    currentPage,
    pageSize,
    totalIssues,
    batchProgress,
    viewMode,
    importedNotices,
    selectedNoticeId,
    selectedIssueId,
    noticeIssues,
    // 新增状态
    recognizedNotices,
    recognizedIssues,
    currentRecognizedNoticeId,
    selectedNoticeIds,
    selectedIssueIds,
    editedData,
    validationErrors,
    modifiedRecords,
    importStep,
    importProgress,
    sectionProjectMapping,

    // 计算属性
    hasFile,
    fileName,
    fileSize,
    hasFiles,
    filesCount,
    totalFilesSize,

    // 方法
    setSelectedFile,
    clearSelectedFile,
    importDocument,
    fetchIssues,
    resetImport,
    setSelectedFiles,
    addSelectedFiles,
    removeSelectedFile,
    clearSelectedFiles,
    importBatch,
    resetBatchImport,
    importFiles,
    importSingleFile,
    goToNoticesList,
    selectNotice,
    selectIssue,
    goBackToNotices,
    goBackToUpload,
    // 新增方法
    recognizeDocument,
    previewNotices,
    previewIssues,
    toggleNoticeSelection,
    toggleIssueSelection,
    editRecord,
    updateRecognizedIssue,
    fetchSectionsByProject,
    validateRecord,
    validateAllRecords,
    importSelected,
    resetRecognition,
    updateSectionProject,
    initializeSectionProjectMapping
  }
})

