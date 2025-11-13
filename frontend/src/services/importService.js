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
  }
}

export default importService

