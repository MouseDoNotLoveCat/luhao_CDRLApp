# 铁路工程质量安全监督问题库管理平台 - 前端

## 项目简介

这是 CDRL（铁路工程质量安全监督问题库管理平台）的前端应用，使用 Vue 3 + Vite + Element Plus 构建。

## 技术栈

- **框架**: Vue 3
- **构建工具**: Vite
- **UI 组件库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP 客户端**: Axios

## 项目结构

```
frontend/
├── src/
│   ├── main.js                 # 应用入口
│   ├── App.vue                 # 根组件（主布局）
│   ├── pages/                  # 页面组件
│   │   ├── ImportPage.vue      # 导入页面
│   │   ├── IssuesPage.vue      # 问题库页面
│   │   └── IssueDetailPage.vue # 问题详情页面
│   ├── components/             # 可复用组件
│   │   └── IssuesTable.vue     # 问题表格组件
│   ├── services/               # API 服务
│   │   ├── api.js              # Axios 实例
│   │   └── importService.js    # 导入相关 API
│   ├── stores/                 # Pinia 状态管理
│   │   └── importStore.js      # 导入状态
│   ├── router/                 # 路由配置
│   │   └── index.js            # 路由定义
│   └── assets/                 # 静态资源
├── index.html                  # HTML 入口
├── vite.config.js              # Vite 配置
└── package.json                # 项目依赖
```

## 安装和运行

### 前置要求

- Node.js >= 18.0.0
- npm 或 yarn

### 安装依赖

```bash
cd frontend
npm install
```

### 开发模式

```bash
npm run dev
```

应用将在 `http://localhost:3000` 启动，并自动代理 API 请求到 `http://localhost:8000`。

### 生产构建

```bash
npm run build
```

构建输出将在 `dist/` 目录中。

### 预览生产构建

```bash
npm run preview
```

## 功能说明

### 1. 导入监督检查通知书

- 支持拖拽或点击选择 .docx 文件
- 显示文件信息（名称、大小）
- 点击"开始导入"按钮导入文件
- 显示导入结果（通知书信息、问题统计）
- 显示导入的问题列表

### 2. 工程质量安全问题库

- 显示所有问题的统计信息（总数、质量问题、安全问题、管理问题）
- 问题列表表格，支持：
  - 搜索（按项目名称、工点名称、问题描述）
  - 筛选（按问题类型）
  - 分页（每页 10/20/50/100 条）
  - 排序
  - 点击行查看详情

### 3. 问题详情页面

- 显示问题的所有字段信息
- 分组显示（基本信息、问题信息、检查依据、整改信息、其他信息）
- 返回按钮返回列表

## API 集成

前端通过以下 API 与后端通信：

### 导入相关

- `POST /api/import/document` - 导入单个文档
- `POST /api/import/batch` - 批量导入文档

### 查询相关

- `GET /api/statistics` - 获取统计信息
- `GET /api/notices` - 获取通知书列表
- `GET /api/issues` - 获取问题列表（支持分页和筛选）
- `GET /api/issues/{issue_id}` - 获取问题详情

## 配置

### API 基础 URL

在 `src/services/api.js` 中配置：

```javascript
const API_BASE_URL = 'http://localhost:8000/api'
```

### 开发服务器代理

在 `vite.config.js` 中配置：

```javascript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '/api'),
    },
  },
}
```

## 设计风格

- **配色方案**: 紫色渐变主题（#667eea - #764ba2）
- **布局**: 左侧菜单 + 右侧内容区
- **组件**: 使用 Element Plus 组件库
- **响应式**: 支持不同屏幕尺寸

## 浏览器支持

- Chrome (最新版本)
- Firefox (最新版本)
- Safari (最新版本)
- Edge (最新版本)

## 常见问题

### Q: 如何修改 API 地址？

A: 修改 `src/services/api.js` 中的 `API_BASE_URL` 变量。

### Q: 如何添加新的页面？

A: 
1. 在 `src/pages/` 中创建新的 .vue 文件
2. 在 `src/router/index.js` 中添加路由
3. 在 `src/App.vue` 中添加菜单项

### Q: 如何修改样式？

A: 
- 全局样式在 `src/main.js` 中导入的 Element Plus CSS
- 组件样式在各组件的 `<style scoped>` 中
- 可以在 `vite.config.js` 中配置 Element Plus 主题

## 开发建议

1. 使用 Vue DevTools 浏览器扩展进行调试
2. 使用 Pinia DevTools 查看状态管理
3. 在浏览器开发者工具中查看网络请求
4. 定期运行 `npm run build` 检查构建是否成功

## 许可证

MIT

