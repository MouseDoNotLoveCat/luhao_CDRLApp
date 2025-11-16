import axios from 'axios'

// 使用相对路径，让 Vite 代理处理
const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000  // 增加到 300 秒（5 分钟），防止大文件处理超时
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 只在不是 FormData 时设置 Content-Type
    if (!(config.data instanceof FormData)) {
      config.headers['Content-Type'] = 'application/json'
    }

    console.log('📤 发送 API 请求:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      baseURL: config.baseURL,
      timeout: config.timeout,
      headers: config.headers
    })

    return config
  },
  error => {
    console.error('❌ 请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    console.log('✅ API 响应成功:', {
      status: response.status,
      statusText: response.statusText,
      url: response.config.url,
      data: response.data
    })
    return response.data
  },
  error => {
    console.error('❌ API 请求失败:', {
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      data: error.response?.data,
      headers: error.response?.headers
    })
    return Promise.reject(error)
  }
)

export default api

