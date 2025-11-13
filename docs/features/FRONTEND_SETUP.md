# 前端项目启动指南

## 📋 项目概述

这是 CDRL（铁路工程质量安全监督问题库管理平台）的完整前端应用。

**应用名称**: 铁路工程质量安全监督问题库管理平台

**技术栈**:
- Vue 3 + Vite
- Element Plus UI 组件库
- Pinia 状态管理
- Vue Router 路由
- Axios HTTP 客户端

## 🚀 快速启动

### 前置要求

- Node.js >= 18.0.0（推荐）
- npm 或 yarn
- 后端 FastAPI 服务运行在 `http://localhost:8000`

### 步骤 1: 启动后端服务

```bash
# 在项目根目录
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端服务将在 `http://localhost:8000` 启动。

### 步骤 2: 启动前端开发服务器

```bash
# 在项目根目录
cd frontend
npm install  # 如果还没有安装依赖
npm run dev
```

前端应用将在 `http://localhost:3000` 启动。

### 步骤 3: 打开浏览器

访问 `http://localhost:3000` 即可使用应用。

## 📁 项目结构

```
frontend/
├── src/
│   ├── main.js                 # 应用入口
│   ├── App.vue                 # 根组件（主布局）
│   ├── pages/                  # 页面组件
│   │   ├── ImportPage.vue      # 导入监督检查通知书
│   │   ├── IssuesPage.vue      # 工程质量安全问题库
│   │   └── IssueDetailPage.vue # 问题详情页面
│   ├── components/             # 可复用组件
│   │   └── IssuesTable.vue     # 问题表格组件
│   ├── services/               # API 服务
│   │   ├── api.js              # Axios 实例配置
│   │   └── importService.js    # 导入相关 API
│   ├── stores/                 # Pinia 状态管理
│   │   └── importStore.js      # 导入状态管理
│   ├── router/                 # 路由配置
│   │   └── index.js            # 路由定义
│   └── assets/                 # 静态资源
├── index.html                  # HTML 入口
├── vite.config.js              # Vite 配置
├── package.json                # 项目依赖
└── README.md                   # 详细文档
```

## 🎨 主要功能

### 1. 导入监督检查通知书

**路径**: 左侧菜单 → "导入监督检查通知书"

**功能**:
- 拖拽或点击选择 .docx 文件
- 显示文件信息（名称、大小）
- 点击"开始导入"按钮导入文件
- 显示导入结果（通知书编号、检查日期、检查单位、检查人员）
- 显示问题统计（质量问题、安全问题、管理问题、总数）
- 显示导入的问题列表

### 2. 工程质量安全问题库

**路径**: 左侧菜单 → "工程质量安全问题库"

**功能**:
- 显示统计卡片（问题总数、质量问题、安全问题、管理问题）
- 问题列表表格，支持：
  - 搜索（按项目名称、工点名称、问题描述）
  - 筛选（按问题类型）
  - 分页（每页 10/20/50/100 条）
  - 排序
  - 点击行查看详情

### 3. 问题详情页面

**路径**: 从问题列表点击"详情"按钮进入

**功能**:
- 显示问题的所有字段信息
- 分组显示（基本信息、问题信息、检查依据、整改信息、其他信息）
- 返回按钮返回列表

## 🔧 配置

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

## 📦 可用的 npm 命令

```bash
# 开发模式（带热重载）
npm run dev

# 生产构建
npm run build

# 预览生产构建
npm run preview
```

## 🌐 API 端点

前端使用以下 API 端点与后端通信：

### 导入相关

- `POST /api/import/document` - 导入单个文档
- `POST /api/import/batch` - 批量导入文档

### 查询相关

- `GET /api/statistics` - 获取统计信息
- `GET /api/notices` - 获取通知书列表
- `GET /api/issues` - 获取问题列表（支持分页和筛选）
- `GET /api/issues/{issue_id}` - 获取问题详情

## 🎯 使用流程

### 新用户入门（约 5 分钟）

1. 启动后端服务
2. 启动前端开发服务器
3. 打开浏览器访问 `http://localhost:3000`
4. 点击"导入监督检查通知书"
5. 选择 `Samples/` 目录下的 .docx 文件
6. 点击"开始导入"
7. 查看导入结果和问题列表
8. 点击问题行查看详情

### 日常使用流程

1. 导入新的监督检查通知书
2. 查看问题库中的所有问题
3. 搜索或筛选特定问题
4. 查看问题详情

## 🐛 常见问题

### Q: 前端无法连接到后端

**A**: 
1. 确保后端服务运行在 `http://localhost:8000`
2. 检查 `src/services/api.js` 中的 API 基础 URL
3. 检查浏览器控制台的网络请求

### Q: 导入文件失败

**A**:
1. 确保文件是 .docx 格式
2. 检查文件是否损坏
3. 查看浏览器控制台的错误信息

### Q: 页面加载缓慢

**A**:
1. 检查网络连接
2. 检查后端服务是否正常运行
3. 尝试清除浏览器缓存

## 📝 开发建议

1. 使用 Vue DevTools 浏览器扩展进行调试
2. 使用 Pinia DevTools 查看状态管理
3. 在浏览器开发者工具中查看网络请求
4. 定期运行 `npm run build` 检查构建是否成功

## 🚀 生产部署

### 构建生产版本

```bash
npm run build
```

### 部署到服务器

1. 将 `dist/` 目录中的文件上传到服务器
2. 配置 Web 服务器（如 Nginx）指向 `dist/` 目录
3. 配置 API 代理指向后端服务

### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /path/to/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📞 支持

如有问题，请查看：
- 前端 README: `frontend/README.md`
- 后端文档: `backend/README.md`
- 数据库文档: `DATABASE_SCHEMA.md`

## 📄 许可证

MIT

