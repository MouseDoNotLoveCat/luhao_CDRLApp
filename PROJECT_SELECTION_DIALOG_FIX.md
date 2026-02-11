# 项目选择对话框修复说明

## 🐛 问题描述

### 现象
1. **项目列表为空**：打开项目选择对话框时，下拉列表无法显示任何项目
2. **创建项目提示重复**：尝试创建已存在的项目时提示"项目名称已存在"，说明后端能检测到项目，但前端无法显示

## 🔍 根本原因

### 问题 1：API 实例使用错误
**位置**：`ProjectSelectionDialog.vue` 第 74 行

**错误代码**：
```javascript
import axios from 'axios'
// ...
const response = await axios.get('/api/projects', {
  params: { limit: 1000 }
})
```

**问题**：
- 直接使用 `axios` 而不是配置好的 `api` 实例
- 导致请求没有经过拦截器处理
- 可能缺少必要的配置（baseURL、timeout 等）

### 问题 2：响应数据格式不匹配
**位置**：`ProjectSelectionDialog.vue` 第 121 行

**错误代码**：
```javascript
projects.value = response.data.items || []
```

**后端实际返回格式**：
```javascript
{
  total: 10,
  data: [
    { id: 1, project_name: '玉岑铁路', builder_unit: '...', sections_count: 3 },
    // ...
  ]
}
```

**问题**：
- 前端期望 `response.data.items`
- 后端实际返回 `response.data`（因为 api 拦截器已经提取了 `response.data`）
- 数据字段是 `data` 而不是 `items`

### 问题 3：创建项目响应处理错误
**位置**：`ProjectSelectionDialog.vue` 第 175-178 行

**错误代码**：
```javascript
emit('confirm', {
  project_id: response.data.id,  // ❌ 多了一层 .data
  project_name: response.data.project_name,
  builder_unit: response.data.builder_unit
})
```

**问题**：
- api 拦截器已经返回 `response.data`
- 这里又访问 `response.data.xxx` 导致取值错误

## ✅ 修复方案

### 修复 1：使用配置好的 API 实例
```javascript
// ❌ 错误
import axios from 'axios'
const response = await axios.get('/api/projects', ...)

// ✅ 正确
import api from '@/services/api'
const response = await api.get('/projects', ...)
```

**好处**：
- 自动添加 baseURL（`/api`）
- 经过请求/响应拦截器处理
- 统一的错误处理和日志记录
- 自动提取 `response.data`

### 修复 2：正确解析响应数据
```javascript
// ❌ 错误
projects.value = response.data.items || []

// ✅ 正确
projects.value = response.data || []
```

**说明**：
- `api.get()` 返回的已经是 `response.data`（经过拦截器处理）
- 后端返回 `{ total, data }`，所以访问 `response.data` 获取项目数组

### 修复 3：正确处理创建项目响应
```javascript
// ❌ 错误
emit('confirm', {
  project_id: response.data.id,
  project_name: response.data.project_name,
  builder_unit: response.data.builder_unit
})

// ✅ 正确
emit('confirm', {
  project_id: response.id,
  project_name: response.project_name,
  builder_unit: response.builder_unit
})
```

### 修复 4：添加调试日志
```javascript
const fetchProjects = async () => {
  try {
    console.log('🔍 开始获取项目列表...')
    const response = await api.get('/projects', {
      params: { limit: 1000 }
    })
    console.log('📥 项目列表响应:', response)
    projects.value = response.data || []
    console.log('✅ 项目列表加载成功，共', projects.value.length, '个项目')
  } catch (error) {
    console.error('❌ 获取项目列表失败:', error)
    ElMessage.error('获取项目列表失败')
  }
}
```

## 📝 修改的文件

- `frontend/src/components/ProjectSelectionDialog.vue`
  - 第 74 行：导入 `api` 而不是 `axios`
  - 第 118 行：使用 `api.get('/projects', ...)` 而不是 `axios.get('/api/projects', ...)`
  - 第 121 行：修改为 `response.data` 而不是 `response.data.items`
  - 第 167 行：使用 `api.post('/projects', ...)` 而不是 `axios.post('/api/projects', ...)`
  - 第 175-178 行：修改为 `response.xxx` 而不是 `response.data.xxx`
  - 添加详细的调试日志

## 🎯 预期效果

修复后：
1. ✅ 打开项目选择对话框时，下拉列表正确显示所有项目
2. ✅ 项目显示格式：`项目名称 (建设单位)`
3. ✅ 可以从列表中选择现有项目
4. ✅ 可以创建新项目（如果项目名称不存在）
5. ✅ 创建重复项目时显示正确的错误提示
6. ✅ 控制台显示详细的调试日志，便于排查问题

## 🧪 测试建议

1. **打开对话框测试**：
   - 点击"批量设置项目"按钮
   - 检查控制台日志：`🔍 开始获取项目列表...`
   - 检查控制台日志：`✅ 项目列表加载成功，共 X 个项目`
   - 检查下拉列表是否显示项目

2. **选择现有项目测试**：
   - 从下拉列表选择一个项目
   - 点击"确定"
   - 验证标段的项目是否更新

3. **创建新项目测试**：
   - 输入新的项目名称和建设单位
   - 点击"确定"
   - 检查控制台日志：`✅ 项目创建成功`
   - 验证项目是否创建成功

4. **创建重复项目测试**：
   - 输入已存在的项目名称
   - 点击"确定"
   - 验证是否显示"项目名称已存在"错误提示

## 📚 相关知识点

### API 拦截器的作用
`frontend/src/services/api.js` 中的响应拦截器：
```javascript
api.interceptors.response.use(
  response => {
    console.log('✅ API 响应成功:', response)
    return response.data  // ⭐ 自动提取 response.data
  },
  // ...
)
```

**重要**：因为拦截器返回 `response.data`，所以：
- `api.get()` 返回的是 `response.data`，而不是完整的 `response`
- 在组件中使用时，直接访问 `response.xxx`，而不是 `response.data.xxx`

---

**修复日期**：2026-02-07  
**问题类型**：API 调用错误、数据格式不匹配  
**影响范围**：项目选择对话框  
**状态**：✅ 已修复

