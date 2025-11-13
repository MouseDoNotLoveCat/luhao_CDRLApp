import axios from 'axios'

// 使用相对路径，让 Vite 代理处理
const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 只在不是 FormData 时设置 Content-Type
    if (!(config.data instanceof FormData)) {
      config.headers['Content-Type'] = 'application/json'
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    console.log('API Response:', response.data)
    return response.data
  },
  error => {
    console.error('API Error:', error)
    console.error('Error response:', error.response)
    return Promise.reject(error)
  }
)

export default api

