# 项目与标段管理 - 快速参考卡片

**版本**: 1.0 | **日期**: 2025-11-07

---

## 🚀 快速启动

```bash
# 启动后端
cd backend && python -m uvicorn app.main:app --reload --port 8000

# 启动前端
cd frontend && npm run dev

# 访问应用
http://localhost:3000
```

---

## 📋 功能速查表

### 项目管理

| 功能 | 操作 | 快捷键 |
|------|------|--------|
| 查看项目列表 | 点击菜单"项目与标段管理" | - |
| 搜索项目 | 在搜索框输入关键词 | - |
| 新建项目 | 点击"➕ 新建项目" | - |
| 编辑项目 | 点击项目行的"编辑" | - |
| 删除项目 | 点击项目行的"删除" | - |
| 查看标段 | 点击项目行的"查看标段" | - |

### 标段管理

| 功能 | 操作 | 快捷键 |
|------|------|--------|
| 查看标段列表 | 从项目列表点击"查看标段" | - |
| 搜索标段 | 在搜索框输入关键词 | - |
| 新建标段 | 点击"➕ 新建标段" | - |
| 编辑标段 | 点击标段行的"编辑" | - |
| 删除标段 | 点击标段行的"删除" | - |
| 返回项目列表 | 点击"← 返回项目列表" | - |

---

## 🔌 API 速查表

### 项目 API

```bash
# 获取项目列表
GET /api/projects?search=&limit=100&offset=0

# 创建项目
POST /api/projects?project_name=新项目&builder_unit=建设单位

# 获取单个项目
GET /api/projects/{project_id}

# 修改项目
PUT /api/projects/{project_id}?project_name=修改后的项目

# 删除项目
DELETE /api/projects/{project_id}?cascade=false
```

### 标段 API

```bash
# 获取标段列表
GET /api/projects/{project_id}/sections?search=&limit=100&offset=0

# 创建标段
POST /api/sections?project_id=1&section_code=QFSG-1&section_name=标段1

# 获取单个标段
GET /api/sections/{section_id}

# 修改标段
PUT /api/sections/{section_id}?section_code=MODIFIED-1

# 删除标段
DELETE /api/sections/{section_id}
```

---

## 📊 数据结构

### 项目对象

```json
{
  "id": 1,
  "project_name": "黄百铁路广西段",
  "builder_unit": "云桂铁路广西有限责任公司",
  "sections_count": 5,
  "created_at": "2025-11-07 07:29:23",
  "updated_at": "2025-11-07 07:29:23"
}
```

### 标段对象

```json
{
  "id": 24,
  "project_id": 1,
  "section_code": "QFSG-1",
  "section_name": "标段 1",
  "contractor_unit": "施工单位",
  "supervisor_unit": "监理单位",
  "designer_unit": "设计单位",
  "testing_unit": "检测单位",
  "created_at": "2025-11-07 07:29:23",
  "updated_at": "2025-11-07 07:29:23"
}
```

---

## 🎯 常见操作

### 创建项目和标段

```bash
# 1. 创建项目
curl -X POST "http://localhost:8000/api/projects" \
  -d "project_name=新项目&builder_unit=建设单位"

# 2. 创建标段（假设项目 ID 为 1）
curl -X POST "http://localhost:8000/api/sections" \
  -d "project_id=1&section_code=QFSG-1&section_name=标段1"
```

### 搜索和过滤

```bash
# 搜索项目
curl "http://localhost:8000/api/projects?search=黄百"

# 搜索标段
curl "http://localhost:8000/api/projects/1/sections?search=QFSG"

# 分页查询
curl "http://localhost:8000/api/projects?limit=20&offset=0"
```

### 删除操作

```bash
# 删除标段
curl -X DELETE "http://localhost:8000/api/sections/24"

# 删除项目（不级联）
curl -X DELETE "http://localhost:8000/api/projects/1?cascade=false"

# 删除项目（级联删除标段）
curl -X DELETE "http://localhost:8000/api/projects/1?cascade=true"
```

---

## ⚠️ 注意事项

| 项目 | 说明 |
|------|------|
| **项目名称** | 全局唯一，不能重复 |
| **标段编号** | 同一项目下唯一 |
| **级联删除** | 删除项目时可选择是否删除其下所有标段 |
| **搜索** | 模糊匹配，不区分大小写 |
| **分页** | 默认每页 20 条，可自定义 |

---

## 🐛 常见问题

| 问题 | 解决方案 |
|------|--------|
| 无法连接后端 | 确保后端运行在 http://localhost:8000 |
| 项目名称重复 | 项目名称必须唯一，修改名称后重试 |
| 删除项目失败 | 项目下有标段，选择级联删除或先删除标段 |
| 搜索无结果 | 检查搜索关键词是否正确 |

---

## 📁 文件位置

| 文件 | 位置 |
|------|------|
| 主页面 | `frontend/src/pages/ProjectManagementPage.vue` |
| 项目列表 | `frontend/src/components/ProjectsList.vue` |
| 标段列表 | `frontend/src/components/SectionsList.vue` |
| 项目表单 | `frontend/src/components/ProjectForm.vue` |
| 标段表单 | `frontend/src/components/SectionForm.vue` |
| 状态管理 | `frontend/src/stores/projectManagementStore.js` |
| 后端 API | `backend/app/main.py` (第 304-871 行) |
| 数据库 | `backend/cdrl.db` |

---

## 📞 获取帮助

- 📖 [完整实现文档](../features/PROJECT_MANAGEMENT_IMPLEMENTATION.md)
- 🚀 [快速开始指南](./PROJECT_MANAGEMENT_QUICK_START.md)
- 🔌 [API 参考文档](./PROJECT_MANAGEMENT_API_REFERENCE.md)
- 🧪 [测试指南](../testing/PROJECT_MANAGEMENT_TEST_GUIDE.md)

---

**最后更新**: 2025-11-07


