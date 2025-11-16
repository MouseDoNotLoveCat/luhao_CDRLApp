import api from './api'

export const importService = {
  // 导入单个文档
  async importDocument(file) {
    const formData = new FormData()
    formData.append('file', file)

    // 不要手动设置 Content-Type，让 axios 自动处理
    // axios 会自动设置正确的 multipart/form-data 和 boundary
    return api.post('/import/document', formData)
  },

  // 批量导入文档
  async importBatch(files) {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })

    // 不要手动设置 Content-Type，让 axios 自动处理
    return api.post('/import/batch', formData)
  },

  // 获取统计信息
  async getStatistics() {
    return api.get('/statistics')
  },

  // 获取通知书列表
  async getNotices(limit = 10, offset = 0) {
    return api.get('/notices', {
      params: { limit, offset }
    })
  },

  // 获取问题列表
  async getIssues(limit = 20, offset = 0, isRectification = null) {
    const params = { limit, offset }
    if (isRectification !== null) {
      params.is_rectification = isRectification
    }
    return api.get('/issues', { params })
  },

  // 获取问题详情
  async getIssueDetail(issueId) {
    return api.get(`/issues/${issueId}`)
  },

  // 识别文档（只识别不导入）
  async recognizeDocument(file) {
    const formData = new FormData()
    formData.append('file', file)

    console.log('📤 发送识别请求:', {
      url: '/import/recognize',
      fileName: file.name,
      fileSize: file.size,
      fileType: file.type,
      timeout: '300000ms (5分钟)'
    })

    try {
      const response = await api.post('/import/recognize', formData)
      console.log('📥 收到识别响应:', response)
      return response
    } catch (error) {
      console.error('❌ 识别请求失败:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        message: error.message,
        code: error.code
      })

      // 检查是否是超时错误
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        console.error('⏱️  请求超时：文件处理耗时过长，请稍候...')
      }

      throw error
    }
  },

  // 导入选中的问题
  async importSelected(noticeData, selectedIssueIds) {
    return api.post('/import/selected', {
      notice_data: noticeData,
      selected_issue_ids: selectedIssueIds
    })
  }
}

export default importService

