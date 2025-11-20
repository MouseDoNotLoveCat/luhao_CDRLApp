# 快速参考指南

## 🚀 快速启动

```bash
# 启动前端开发服务器
cd frontend
npm install  # 首次运行
npm run dev  # 启动开发服务器 (http://localhost:3000)

# 启动后端服务器（另一个终端）
cd backend
python app/main.py  # 启动 FastAPI (http://localhost:8000)
```

## 📁 关键文件位置

### Frontend
- **主入口**: `frontend/src/main.js`
- **根组件**: `frontend/src/App.vue`
- **路由配置**: `frontend/src/router/index.js`
- **API 配置**: `frontend/src/services/api.js`

### Backend
- **主入口**: `backend/app/main.py`
- **数据库**: `backend/cdrl.db`
- **解析器**: `backend/app/parsers/`

## 🎯 主要功能页面

| 页面 | 路由 | 文件 | 功能 |
|------|------|------|------|
| 导入 | `/import` | ImportPage.vue | 导入 Word 文档 |
| 问题列表 | `/issues` | IssuesPage.vue | 查看所有问题 |
| 问题详情 | `/issues/:id` | IssueDetailPage.vue | 查看问题详情 |
| 通知书管理 | `/notices` | NoticeManagementPage.vue | 管理通知书 |
| 项目管理 | `/projects` | ProjectManagementPage.vue | 管理项目 |

## 🔧 常见操作

### 添加新页面
1. 在 `frontend/src/pages/` 创建 `.vue` 文件
2. 在 `frontend/src/router/index.js` 添加路由
3. 在 `frontend/src/App.vue` 添加导航链接

### 添加新组件
1. 在 `frontend/src/components/` 创建 `.vue` 文件
2. 在需要的页面中导入和使用

### 添加新状态管理
1. 在 `frontend/src/stores/` 创建 `.js` 文件
2. 使用 Pinia 的 `defineStore` 定义
3. 在组件中使用 `useXxxStore()`

## 📊 数据库表

### 主要表
- **supervision_notices** - 监督检查通知书
- **projects** - 项目信息
- **sections** - 分项信息
- **issues** - 问题信息

### 关键字段
- `issue_id` - 问题唯一标识
- `supervision_notice_id` - 关联的通知书
- `section_id` - 关联的分项
- `responsible_person` - 责任人

## 🐛 调试技巧

### 查看浏览器控制台
- 打开浏览器开发者工具 (F12)
- 查看 Console 标签页的错误信息
- 查看 Network 标签页的 API 请求

### 查看 Vite 编译错误
- 查看终端输出
- 检查 `frontend/src/` 中的文件语法

### 查看 FastAPI 错误
- 查看后端终端输出
- 访问 `http://localhost:8000/docs` 查看 API 文档

## 📝 文件修改检查清单

修改文件后，检查以下项目：
- [ ] 文件有 `<template>` 和 `<script>` 标签（Vue 文件）
- [ ] 导入语句正确
- [ ] 没有语法错误
- [ ] 浏览器控制台无错误
- [ ] 功能正常工作

## 🗑️ 已删除的文件

- `frontend/src/components/MatchingResultAlert.vue` - 空文件
- `frontend/src/components/NoticesList.vue` - 空文件（由 NoticesListComponent.vue 替代）

## 📚 相关文档

- `PROJECT_STRUCTURE_DIAGNOSIS_REPORT.md` - 诊断报告
- `PROJECT_ARCHITECTURE_DOCUMENTATION.md` - 架构文档
- `COMPONENT_DEPENDENCY_ANALYSIS.md` - 依赖关系分析

