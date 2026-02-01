# CDRLApp 前后端架构文档

## 📋 目录

- [项目概述](#项目概述)
- [技术栈](#技术栈)
- [前端架构](#前端架构)
- [后端架构](#后端架构)
- [前后端交互流程](#前后端交互流程)
- [数据流图](#数据流图)

---

## 项目概述

**CDRLApp** 是一个铁路工程质量安全监督问题库管理平台，用于：
- 导入和识别监督检查通知书（Word 文档）
- 管理工程质量安全问题
- 管理项目和标段信息
- 查看和分析问题统计数据

---

## 技术栈

### 前端
- **框架**: Vue 3 (Composition API)
- **UI 组件库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP 客户端**: Axios
- **构建工具**: Vite

### 后端
- **框架**: FastAPI (Python)
- **数据库**: SQLite
- **ORM**: SQLAlchemy
- **文档解析**: python-docx
- **服务器**: Uvicorn

---

## 前端架构

### 1. 目录结构

```
frontend/src/
├── main.js                 # 应用入口
├── App.vue                 # 根组件（主布局）
├── pages/                  # 页面组件（路由级别）
│   ├── ImportPage.vue      # 导入页面
│   ├── IssuesPage.vue      # 问题库页面
│   ├── IssueDetailPage.vue # 问题详情页面
│   ├── ProjectManagementPage.vue   # 项目管理页面
│   └── NoticeManagementPage.vue    # 通知书管理页面
├── components/             # 可复用组件
│   ├── ImportPreviewNotices.vue    # 导入-预览通知书
│   ├── ImportPreviewIssues.vue     # 导入-预览问题
│   ├── ImportIssuesEditor.vue      # 导入-编辑问题
│   ├── ImportConfirm.vue           # 导入-确认导入
│   ├── ImportResult.vue            # 导入-导入结果
│   ├── IssuesTable.vue             # 问题表格
│   ├── NoticesList.vue             # 通知书列表
│   ├── ProjectsList.vue            # 项目列表
│   └── SectionsList.vue            # 标段列表
├── stores/                 # Pinia 状态管理
│   ├── importStore.js      # 导入相关状态
│   ├── noticeManagementStore.js    # 通知书管理状态
│   └── projectManagementStore.js   # 项目管理状态
├── services/               # API 服务
│   ├── api.js              # Axios 实例配置
│   └── importService.js    # 导入相关 API
├── router/                 # 路由配置
│   └── index.js            # 路由定义
└── config/                 # 配置文件
    └── issueCategories.js  # 问题分类配置
```

### 2. 页面组成

#### 2.1 导入页面 (`ImportPage.vue`)

**功能**: 导入监督检查通知书，识别问题

**视图模式**:
- `upload`: 文件上传界面
- `recognizing`: 识别中
- `preview-notices`: 预览通知书
- `preview-issues`: 预览问题列表
- `edit-issues`: 编辑问题
- `confirm`: 确认导入
- `importing`: 导入中
- `result`: 导入结果

**使用的组件**:
- `ImportPreviewNotices.vue` - 预览识别的通知书信息
- `ImportPreviewIssues.vue` - 预览识别的问题列表（带选择功能）
- `ImportIssuesEditor.vue` - 编辑问题信息（标段、工点、分类等）
- `ImportConfirm.vue` - 确认导入前的最后检查
- `ImportResult.vue` - 显示导入结果

**状态管理**: `importStore`

---

#### 2.2 问题库页面 (`IssuesPage.vue`)

**功能**: 查看和管理所有问题

**主要功能**:
- 显示问题统计（总数、质量问题、安全问题、管理问题）
- 问题列表（支持搜索、筛选、分页、排序）
- 点击问题查看详情

**使用的组件**:
- `IssuesTable.vue` - 问题表格组件

**状态管理**: `importStore`

---

#### 2.3 问题详情页面 (`IssueDetailPage.vue`)

**功能**: 查看单个问题的详细信息

**显示内容**:
- 基本信息（标段、工点、施工单位、监理单位）
- 问题描述
- 问题分类（一级、二级、三级）
- 检查信息（检查单位、检查时间、检查人员）
- 整改信息（整改要求、整改期限、责任单位）

**状态管理**: `importStore`

---

#### 2.4 项目管理页面 (`ProjectManagementPage.vue`)

**功能**: 管理项目和标段

**主要功能**:
- 项目列表（增删改查）
- 标段列表（增删改查）
- 项目-标段关联管理

**使用的组件**:
- `ProjectsList.vue` - 项目列表
- `SectionsList.vue` - 标段列表
- `ProjectForm.vue` - 项目表单
- `SectionForm.vue` - 标段表单

**状态管理**: `projectManagementStore`

---

#### 2.5 通知书管理页面 (`NoticeManagementPage.vue`)

**功能**: 管理监督检查通知书

**主要功能**:
- 通知书列表（查看、删除）
- 查看通知书详情
- 查看通知书关联的问题

**使用的组件**:
- `NoticesList.vue` - 通知书列表
- `IssuesPreview.vue` - 问题预览
- `IssueDetailPreview.vue` - 问题详情预览

**状态管理**: `noticeManagementStore`

---

### 3. 状态管理 (Pinia Stores)

#### 3.1 importStore

**职责**: 管理文档导入和问题数据

**主要状态**:
```javascript
{
  selectedFiles: [],              // 选中的文件
  isLoading: false,               // 加载状态
  importResult: null,             // 导入结果
  issues: [],                     // 问题列表
  viewMode: 'upload',             // 视图模式
  recognizedNotices: [],          // 识别的通知书
  recognizedIssues: [],           // 识别的问题
  selectedIssueIds: Set,          // 选中的问题 ID
}
```

**主要方法**:
- `recognizeDocument()` - 识别文档
- `importSelected()` - 导入选中的问题
- `fetchIssues()` - 获取问题列表
- `fetchIssueDetail()` - 获取问题详情

---

#### 3.2 noticeManagementStore

**职责**: 管理通知书数据

**主要状态**:
```javascript
{
  notices: [],                    // 通知书列表
  selectedNotice: null,           // 选中的通知书
  noticeIssues: [],               // 通知书的问题列表
  viewMode: 'list',               // 视图模式
}
```

**主要方法**:
- `fetchNotices()` - 获取通知书列表
- `fetchNoticeDetail()` - 获取通知书详情
- `deleteNotice()` - 删除通知书

---

#### 3.3 projectManagementStore

**职责**: 管理项目和标段数据

**主要状态**:
```javascript
{
  projects: [],                   // 项目列表
  sections: [],                   // 标段列表
  selectedProjectId: null,        // 选中的项目 ID
}
```

**主要方法**:
- `fetchProjects()` - 获取项目列表
- `fetchSections()` - 获取标段列表
- `createProject()` - 创建项目
- `updateProject()` - 更新项目
- `deleteProject()` - 删除项目
- `createSection()` - 创建标段
- `updateSection()` - 更新标段
- `deleteSection()` - 删除标段

---

### 4. API 服务层

#### 4.1 api.js

**职责**: Axios 实例配置

**配置**:
- Base URL: `/api` (由 Vite 代理到 `http://localhost:8000`)
- Timeout: 300 秒（5 分钟）
- 请求/响应拦截器（日志记录）

---

#### 4.2 importService.js

**职责**: 封装导入相关的 API 调用

**主要方法**:
```javascript
{
  recognizeDocument(file)         // POST /import/recognize
  importDocument(file)            // POST /import/document
  importBatch(files)              // POST /import/batch
  importSelected(noticeData, ids) // POST /import/selected
  getIssues(limit, offset)        // GET /issues
  getIssueDetail(issueId)         // GET /issues/{id}
}
```

---

## 后端架构

### 1. 目录结构

```
backend/app/
├── main.py                 # FastAPI 应用入口，定义所有 API 端点
├── parsers/                # 文档解析模块
│   ├── word_parser.py      # Word 文档解析器
│   └── enhanced_patterns.py # 增强的正则表达式模式
└── services/               # 业务逻辑服务
    ├── import_service.py   # 导入服务
    ├── issue_category_classifier.py  # 问题分类器
    └── project_section_matcher.py    # 项目标段匹配器
```

### 2. API 端点

#### 2.1 导入相关 API

| 端点 | 方法 | 功能 | 前端调用位置 |
|------|------|------|-------------|
| `/import/recognize` | POST | 识别文档（不导入） | `importStore.recognizeDocument()` |
| `/import/document` | POST | 导入单个文档 | `importStore.importDocument()` |
| `/import/batch` | POST | 批量导入文档 | `importStore.importBatch()` |
| `/import/selected` | POST | 导入选中的问题 | `importStore.importSelected()` |

**请求/响应示例**:

```javascript
// POST /import/recognize
// 请求: FormData { file: File }
// 响应:
{
  "status": "success",
  "notices": [{
    "notice_number": "南宁站〔2026〕（通知）玉岑1号",
    "check_date": "2026-01-21",
    "check_unit": "南宁铁路监督管理局",
    "total_issues_count": 63
  }],
  "issues": [{
    "section_name": "YCZQ-3标",
    "site_name": "大车山中桥无砟轨道工程",
    "contractor": "中铁四局",
    "supervisor": "中铁路安监理",
    "description": "问题描述...",
    "inspection_date": "2026-01-21",
    "issue_category": "质量问题",
    "severity": 3,
    ...
  }]
}
```

---

#### 2.2 问题相关 API

| 端点 | 方法 | 功能 | 前端调用位置 |
|------|------|------|-------------|
| `/issues` | GET | 获取问题列表 | `importStore.fetchIssues()` |
| `/issues/{id}` | GET | 获取问题详情 | `importStore.fetchIssueDetail()` |

**查询参数**:
- `limit`: 每页数量（默认 10）
- `offset`: 偏移量（默认 0）
- `is_rectification`: 是否整改通知（可选）

---

#### 2.3 通知书相关 API

| 端点 | 方法 | 功能 | 前端调用位置 |
|------|------|------|-------------|
| `/notices` | GET | 获取通知书列表 | `noticeManagementStore.fetchNotices()` |
| `/notices/{id}` | GET | 获取通知书详情 | `noticeManagementStore.fetchNoticeDetail()` |
| `/notices/{id}` | DELETE | 删除通知书 | `noticeManagementStore.deleteNotice()` |

---

#### 2.4 项目相关 API

| 端点 | 方法 | 功能 | 前端调用位置 |
|------|------|------|-------------|
| `/projects` | GET | 获取项目列表 | `projectManagementStore.fetchProjects()` |
| `/projects/{id}` | GET | 获取项目详情 | `projectManagementStore.fetchProjectDetail()` |
| `/projects` | POST | 创建项目 | `projectManagementStore.createProject()` |
| `/projects/{id}` | PUT | 更新项目 | `projectManagementStore.updateProject()` |
| `/projects/{id}` | DELETE | 删除项目 | `projectManagementStore.deleteProject()` |

---

#### 2.5 标段相关 API

| 端点 | 方法 | 功能 | 前端调用位置 |
|------|------|------|-------------|
| `/sections` | GET | 根据项目名获取标段 | - |
| `/projects/{id}/sections` | GET | 获取项目的标段列表 | `projectManagementStore.fetchSections()` |
| `/sections/{id}` | GET | 获取标段详情 | - |
| `/sections` | POST | 创建标段 | `projectManagementStore.createSection()` |
| `/sections/{id}` | PUT | 更新标段 | `projectManagementStore.updateSection()` |
| `/sections/{id}` | DELETE | 删除标段 | `projectManagementStore.deleteSection()` |

---

#### 2.6 匹配相关 API

| 端点 | 方法 | 功能 | 说明 |
|------|------|------|------|
| `/match/project` | POST | 匹配项目名 | 根据文档中的项目名匹配数据库中的项目 |
| `/match/section` | POST | 匹配标段 | 根据标段代码匹配数据库中的标段 |

---

### 3. 核心模块

#### 3.1 Word 文档解析器 (`word_parser.py`)

**职责**: 解析 Word 文档，提取通知书和问题信息

**主要函数**:
- `parse_word_document(file_path)` - 主解析函数
- `_extract_notice_metadata()` - 提取通知书元数据
- `_extract_rectification_notices()` - 提取整改通知问题
- `_extract_other_issues()` - 提取其他问题
- `_extract_section_name()` - 提取标段名称
- `_clean_site_name_and_extract_date()` - 清理工点名称并提取检查时间

**支持的文档格式**:
1. **格式 1**（原有格式）: 检查时间在标段后面
   ```
   （一）LWZF-2标（检查时间：2025年8月15日）
   1. 工点名称
   ```

2. **格式 2**（新格式）: 检查时间在工点名称后面
   ```
   （三）YCZQ-3标
   1. 工点名称（检查时间：2026年1月21日）
   ```

**关键特性**:
- ✅ 图片标注过滤（`图1`、`图2` 等不会被识别为问题）
- ✅ 工点名称和检查时间分离
- ✅ 支持所有标段格式（`LWZF-2标`、`YCZQ-3标` 等）
- ✅ 兼容两种文档格式

---

#### 3.2 问题分类器 (`issue_category_classifier.py`)

**职责**: 根据问题描述自动分类

**分类层级**:
1. **一级分类**: 质量问题、安全问题、管理问题
2. **二级分类**: 如"混凝土工程"、"钢筋工程"等
3. **三级分类**: 具体问题类型

---

#### 3.3 项目标段匹配器 (`project_section_matcher.py`)

**职责**: 将文档中的项目名和标段代码匹配到数据库中的记录

**匹配策略**:
- 模糊匹配项目名
- 精确匹配标段代码
- 自动关联施工单位和监理单位

---

### 4. 数据库模型

#### 4.1 通知书表 (notices)

```sql
CREATE TABLE notices (
    id INTEGER PRIMARY KEY,
    notice_number TEXT UNIQUE,
    check_date TEXT,
    check_unit TEXT,
    total_issues_count INTEGER,
    created_at TIMESTAMP
);
```

---

#### 4.2 问题表 (issues)

```sql
CREATE TABLE issues (
    id INTEGER PRIMARY KEY,
    notice_id INTEGER,
    section_name TEXT,
    site_name TEXT,
    contractor TEXT,
    supervisor TEXT,
    description TEXT,
    inspection_date TEXT,
    issue_category TEXT,
    issue_type_level1 TEXT,
    issue_type_level2 TEXT,
    severity INTEGER,
    is_rectification_notice BOOLEAN,
    is_bad_behavior_notice BOOLEAN,
    created_at TIMESTAMP,
    FOREIGN KEY (notice_id) REFERENCES notices(id)
);
```

---

#### 4.3 项目表 (projects)

```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    project_name TEXT UNIQUE,
    builder_unit TEXT,
    created_at TIMESTAMP
);
```

---

#### 4.4 标段表 (sections)

```sql
CREATE TABLE sections (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    section_name TEXT,
    contractor_unit TEXT,
    supervisor_unit TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

---

## 前后端交互流程

### 1. 文档导入流程

```
用户操作                前端                    后端
   │                     │                       │
   ├─ 选择文件 ──────────>│                       │
   │                     │                       │
   ├─ 点击"识别" ────────>│ recognizeDocument()   │
   │                     ├──────────────────────>│ POST /import/recognize
   │                     │                       ├─ 解析 Word 文档
   │                     │                       ├─ 提取通知书信息
   │                     │                       ├─ 提取问题列表
   │                     │                       ├─ 自动分类
   │                     │<──────────────────────┤ 返回识别结果
   │                     │ 存储到 recognizedNotices
   │                     │ 存储到 recognizedIssues
   │<────────────────────┤ 显示预览界面
   │                     │                       │
   ├─ 查看/编辑问题 ─────>│ viewMode = 'edit-issues'
   │                     │                       │
   ├─ 选择要导入的问题 ──>│ selectedIssueIds.add()
   │                     │                       │
   ├─ 点击"确认导入" ────>│ importSelected()      │
   │                     ├──────────────────────>│ POST /import/selected
   │                     │                       ├─ 保存通知书到数据库
   │                     │                       ├─ 保存选中的问题
   │                     │                       ├─ 匹配项目和标段
   │                     │<──────────────────────┤ 返回导入结果
   │<────────────────────┤ 显示导入结果
```

---

### 2. 问题查询流程

```
用户操作                前端                    后端
   │                     │                       │
   ├─ 访问问题库页面 ────>│ fetchIssues()         │
   │                     ├──────────────────────>│ GET /issues?limit=20&offset=0
   │                     │                       ├─ 查询数据库
   │                     │<──────────────────────┤ 返回问题列表
   │<────────────────────┤ 显示问题列表
   │                     │                       │
   ├─ 点击问题 ──────────>│ fetchIssueDetail(id)  │
   │                     ├──────────────────────>│ GET /issues/{id}
   │                     │                       ├─ 查询问题详情
   │                     │<──────────────────────┤ 返回问题详情
   │<────────────────────┤ 显示问题详情
```

---

### 3. 项目管理流程

```
用户操作                前端                    后端
   │                     │                       │
   ├─ 访问项目管理页面 ──>│ fetchProjects()       │
   │                     ├──────────────────────>│ GET /projects
   │                     │<──────────────────────┤ 返回项目列表
   │<────────────────────┤ 显示项目列表
   │                     │                       │
   ├─ 选择项目 ──────────>│ fetchSections(id)     │
   │                     ├──────────────────────>│ GET /projects/{id}/sections
   │                     │<──────────────────────┤ 返回标段列表
   │<────────────────────┤ 显示标段列表
   │                     │                       │
   ├─ 创建标段 ──────────>│ createSection()       │
   │                     ├──────────────────────>│ POST /sections
   │                     │<──────────────────────┤ 返回创建结果
   │<────────────────────┤ 刷新标段列表
```

---

## 数据流图

### 导入流程数据流

```
Word 文档
   │
   ├─> word_parser.py
   │      ├─> 提取通知书元数据
   │      ├─> 提取整改通知问题
   │      └─> 提取其他问题
   │
   ├─> issue_category_classifier.py
   │      └─> 自动分类问题
   │
   ├─> project_section_matcher.py
   │      └─> 匹配项目和标段
   │
   └─> 返回识别结果
          │
          ├─> 前端预览
          │      ├─> 用户选择问题
          │      └─> 用户编辑问题
          │
          └─> 保存到数据库
                 ├─> notices 表
                 └─> issues 表
```

---

## 关键技术点

### 1. 文档解析

**挑战**: Word 文档格式多样，需要兼容不同格式

**解决方案**:
- 使用 `python-docx` 逐段解析
- 正则表达式匹配关键信息
- 状态机模式跟踪当前解析上下文
- 启发式规则识别问题描述

---

### 2. 前端状态管理

**挑战**: 导入流程复杂，需要管理多个视图状态

**解决方案**:
- 使用 Pinia 集中管理状态
- `viewMode` 控制视图切换
- 缓存识别结果，避免重复解析
- 用户选择状态独立管理

---

### 3. 数据验证

**挑战**: 识别结果可能不准确，需要用户确认

**解决方案**:
- 三层预览界面（通知书 → 问题列表 → 编辑）
- 用户可编辑所有字段
- 显示检查时间字段便于验证
- 确认界面最后检查

---

## 总结

CDRLApp 采用前后端分离架构：

- **前端**: Vue 3 + Element Plus + Pinia，提供友好的用户界面
- **后端**: FastAPI + SQLite，提供高性能的 API 服务
- **核心功能**: Word 文档解析、问题自动分类、项目标段管理
- **关键特性**: 兼容多种文档格式、用户可编辑识别结果、完整的导入流程

整个系统通过 RESTful API 进行通信，前端通过 Pinia stores 管理状态，后端通过服务层封装业务逻辑，实现了清晰的职责分离和良好的可维护性。

---

**文档版本**: 1.0
**最后更新**: 2026-01-31
