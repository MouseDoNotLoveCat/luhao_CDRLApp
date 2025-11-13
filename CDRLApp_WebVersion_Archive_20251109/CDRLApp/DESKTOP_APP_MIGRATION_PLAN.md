# 铁路工程质量安全监督问题库管理平台 - Web 到桌面应用迁移方案

## 📋 执行摘要

将现有的 FastAPI + Vue Web 应用转换为独立的 Python 桌面应用，保留所有核心功能和数据库。

---

## 第一部分：桌面应用框架选择与方案

### 1. 推荐框架对比

| 框架 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **PyQt6** | 功能完整、界面美观、跨平台、性能好 | 学习曲线陡、依赖较大 | ⭐⭐⭐⭐⭐ |
| **PySimpleGUI** | 简单易用、快速开发 | 功能有限、界面不够专业 | ⭐⭐⭐ |
| **Tkinter** | Python 内置、轻量级 | 界面过时、功能有限 | ⭐⭐ |
| **Kivy** | 跨平台、现代化 | 学习曲线陡、社区较小 | ⭐⭐⭐ |

### 2. 最终选择：PyQt6

**理由：**
- ✅ 功能完整，支持复杂的表格、树形结构、对话框等
- ✅ 界面美观，支持样式表（QSS）自定义
- ✅ 跨平台支持（Windows、macOS、Linux）
- ✅ 性能优秀，适合处理大量数据
- ✅ 社区活跃，文档完善
- ✅ 支持多线程，不会阻塞 UI

---

## 第二部分：核心功能保留方案

### 1. 可直接复用的模块

```
backend/app/parsers/
├── word_parser.py          ✅ 完全复用（Word 文档解析）
├── format_handlers/
│   ├── liuwo_format.py     ✅ 完全复用（柳梧格式）
│   └── huangbai_format.py  ✅ 完全复用（黄百格式）
└── structure_handlers/     ✅ 完全复用（文档结构处理）

backend/app/services/
├── issue_category_classifier.py    ✅ 完全复用（问题分类）
├── project_section_matcher.py      ✅ 完全复用（项目/标段匹配）
└── import_service.py               ⚠️ 部分复用（移除 API 相关代码）
```

### 2. 数据库操作

- ✅ 保留现有 SQLite 数据库结构（`cdrl.db`）
- ✅ 保留所有表结构和约束
- ✅ 直接使用 `sqlite3` 模块（Python 内置）
- ✅ 无需修改数据库初始化脚本

### 3. 业务逻辑层

新建 `services/` 目录，包含：
- `database_service.py` - 数据库操作（CRUD）
- `import_service.py` - 导入逻辑（改进版）
- `issue_service.py` - 问题管理逻辑
- `project_service.py` - 项目管理逻辑

---

## 第三部分：新项目结构设计

### 新项目目录结构

```
CDRLApp_Desktop/
├── main.py                          # 应用入口
├── requirements.txt                 # 依赖列表
├── config.py                        # 配置文件
│
├── ui/                              # UI 层（PyQt6）
│   ├── __init__.py
│   ├── main_window.py              # 主窗口
│   ├── dialogs/
│   │   ├── import_dialog.py        # 导入对话框
│   │   ├── issue_detail_dialog.py  # 问题详情对话框
│   │   └── settings_dialog.py      # 设置对话框
│   ├── widgets/
│   │   ├── issues_table.py         # 问题表格
│   │   ├── notices_list.py         # 通知书列表
│   │   └── issue_preview.py        # 问题预览
│   └── styles/
│       └── style.qss               # 样式表
│
├── services/                        # 业务逻辑层
│   ├── __init__.py
│   ├── database_service.py         # 数据库操作
│   ├── import_service.py           # 导入逻辑
│   ├── issue_service.py            # 问题管理
│   └── project_service.py          # 项目管理
│
├── parsers/                         # 解析器（从 backend 复制）
│   ├── __init__.py
│   ├── word_parser.py
│   ├── format_handlers/
│   │   ├── liuwo_format.py
│   │   └── huangbai_format.py
│   └── structure_handlers/
│
├── classifiers/                     # 分类器（从 backend 复制）
│   ├── __init__.py
│   └── issue_category_classifier.py
│
├── matchers/                        # 匹配器（从 backend 复制）
│   ├── __init__.py
│   └── project_section_matcher.py
│
├── models/                          # 数据模型
│   ├── __init__.py
│   ├── issue.py
│   ├── notice.py
│   └── project.py
│
├── utils/                           # 工具函数
│   ├── __init__.py
│   ├── logger.py
│   └── constants.py
│
├── data/                            # 数据文件
│   ├── cdrl.db                     # SQLite 数据库
│   └── schema.sql                  # 数据库初始化脚本
│
├── resources/                       # 资源文件
│   ├── icons/
│   └── samples/                    # 测试样本
│
└── tests/                           # 测试
    ├── __init__.py
    ├── test_import.py
    └── test_services.py
```

---

## 第四部分：数据迁移方案

### 1. 数据库迁移

**步骤：**
1. 复制现有 `backend/cdrl.db` 到新项目 `data/cdrl.db`
2. 验证数据库完整性
3. 无需修改数据库结构（完全兼容）

### 2. 数据验证

```python
# 验证脚本
def verify_database():
    - 检查所有表是否存在
    - 检查数据完整性
    - 检查外键关系
    - 生成迁移报告
```

### 3. 备份策略

- 自动备份：每次启动时备份数据库
- 手动备份：提供"导出数据"功能
- 版本控制：保留最近 5 个备份

---

## 第五部分：归档方案

### 1. 归档文件夹命名

```
CDRLApp_WebVersion_Archive_20250109/
```

### 2. 归档内容

```
CDRLApp_WebVersion_Archive_20250109/
├── CDRLApp/                    # 完整的 Web 项目
│   ├── backend/
│   ├── frontend/
│   ├── docs/
│   ├── Samples/
│   ├── tests/
│   ├── scripts/
│   ├── database_schema.sql
│   ├── README.md
│   └── [所有其他文件]
│
├── MIGRATION_NOTES.md          # 迁移说明
├── DATABASE_BACKUP.sql         # 数据库备份
└── ARCHIVE_MANIFEST.md         # 归档清单
```

### 3. 验证清单

- [ ] 所有源代码文件
- [ ] 数据库文件（cdrl.db）
- [ ] 文档（docs/）
- [ ] 测试样本（Samples/）
- [ ] 配置文件（package.json、requirements.txt 等）
- [ ] 启动脚本
- [ ] README 和文档

---

## 第六部分：新项目创建步骤

### 1. 初始化

```bash
# 创建新项目目录
mkdir CDRLApp_Desktop
cd CDRLApp_Desktop

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install PyQt6 python-docx sqlite3
```

### 2. 复制核心模块

```bash
# 从归档中复制
cp -r Archive/CDRLApp/backend/app/parsers ./parsers
cp -r Archive/CDRLApp/backend/app/services/issue_category_classifier.py ./classifiers/
cp -r Archive/CDRLApp/backend/app/services/project_section_matcher.py ./matchers/
cp Archive/CDRLApp/backend/cdrl.db ./data/
```

### 3. 创建新的服务层

- 实现 `DatabaseService` - 数据库 CRUD 操作
- 实现 `ImportService` - 改进的导入逻辑
- 实现 `IssueService` - 问题管理
- 实现 `ProjectService` - 项目管理

### 4. 开发 UI 层

- 主窗口（菜单、工具栏、状态栏）
- 导入对话框
- 问题表格和详情
- 项目/标段管理

---

## 第七部分：功能对应关系

### Web 版本 → 桌面版本

| Web 功能 | 桌面版本 | 实现方式 |
|---------|---------|---------|
| 导入通知书 | 导入对话框 | 文件选择 + 进度条 |
| 查看问题列表 | 主表格 | QTableWidget |
| 查看问题详情 | 详情对话框 | QDialog |
| 编辑问题 | 行内编辑 | QTableWidget 代理 |
| 项目管理 | 项目树 | QTreeWidget |
| 数据导出 | 导出菜单 | Excel/CSV/PDF |
| 搜索过滤 | 搜索栏 | QLineEdit + 过滤 |

---

## 第八部分：开发时间表

| 阶段 | 任务 | 预计时间 |
|------|------|---------|
| 1 | 归档 Web 版本 | 1 小时 |
| 2 | 创建项目结构 | 2 小时 |
| 3 | 实现数据库服务 | 4 小时 |
| 4 | 实现导入功能 | 6 小时 |
| 5 | 开发主 UI | 8 小时 |
| 6 | 开发详情 UI | 4 小时 |
| 7 | 测试和调试 | 6 小时 |
| **总计** | | **31 小时** |

---

## 第九部分：风险和缓解措施

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 数据迁移失败 | 数据丢失 | 完整备份 + 验证脚本 |
| PyQt6 学习曲线 | 开发延期 | 使用示例代码 + 文档 |
| 性能问题 | 用户体验差 | 多线程 + 缓存 |
| 跨平台兼容性 | 某些平台崩溃 | 充分测试 + 条件编译 |

---

## 确认清单

请确认以下内容：

- [ ] 同意使用 PyQt6 作为 UI 框架
- [ ] 同意新项目结构设计
- [ ] 同意数据迁移方案
- [ ] 同意归档方案
- [ ] 准备好开始执行

**请确认后，我将开始执行以下步骤：**
1. 创建归档文件夹并移动文件
2. 创建新项目结构
3. 复制核心模块
4. 开始开发桌面应用

