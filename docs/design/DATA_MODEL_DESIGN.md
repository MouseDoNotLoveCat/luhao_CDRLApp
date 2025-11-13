# 📊 数据模型设计文档

## 🎯 需求分析

### 数据来源
1. **监督通知书** (Word 文档)
   - 来源：监督检查现场
   - 格式：.docx 文件
   - 包含：项目信息、检查信息、问题描述、图片等

2. **建设系统安全隐患库** (Excel 文件)
   - 来源：建设部标准模板
   - 格式：.xlsx 文件
   - 包含：隐患信息、整改信息、责任单位等

3. **问题类型分类** (Markdown 文件)
   - 来源：工程质量、施工安全、管理行为等标准分类
   - 用途：未来功能扩展（暂不实现）

### 前期实现范围
- ✅ 实现建设系统安全隐患库的数据结构
- ✅ 支持质量、安全、管理 3 个主类别
- ✅ 安全类别下分 7 个子类别
- ✅ 隐患等级默认为 3 级（一般）
- ⏳ 问题类型详细分类（后期扩展）

---

## 📋 Excel 文件字段映射

### 建设系统安全隐患库（建设部8.7).xlsx 字段

| 序号 | 字段名 | 类型 | 说明 | 必填 |
|------|--------|------|------|------|
| 1 | 序号 | Integer | 隐患编号 | ✅ |
| 2 | 检查时间 | Date | 检查日期 | ✅ |
| 3 | 检查单位 | String | 检查机构 | ✅ |
| 4 | 检查人 | String | 检查人员 | ✅ |
| 5 | 检查项目 | String | 项目名称 | ✅ |
| 6 | 检查工点 | String | 工点名称 | ✅ |
| 7 | 隐患问题描述 | Text | 问题详细描述 | ✅ |
| 8 | 隐患类型 | String | 隐患分类 | ✅ |
| 9 | 隐患等级 | Integer | 隐患等级（1-5） | ✅ |
| 10 | 整改要求（措施） | Text | 整改措施 | ✅ |
| 11 | 整改期限 | Date | 整改截止日期 | ✅ |
| 12 | 整改责任单位 | String | 建设/设计/施工/监理 | ✅ |
| 13 | 整改责任人 | String | 责任人姓名 | ✅ |
| 14 | 整改完成日期 | Date | 实际完成日期 | ⏳ |
| 15 | 销号情况 | String | 已整改/整改完成等 | ⏳ |

---

## 🗄️ 数据库表结构设计

### 1. supervision_notices 表（监督通知书）

```sql
CREATE TABLE supervision_notices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notice_number VARCHAR(100) UNIQUE NOT NULL,  -- 编号
    issue_date DATE,                              -- 签发日期
    check_date DATE NOT NULL,                     -- 检查日期
    check_unit VARCHAR(100),                      -- 检查单位
    check_personnel VARCHAR(200),                 -- 检查人员
    file_path VARCHAR(500),                       -- 原始文件路径
    file_hash VARCHAR(64),                        -- 文件哈希
    total_issues INTEGER DEFAULT 0,               -- 问题总数
    quality_issues INTEGER DEFAULT 0,             -- 质量问题数
    safety_issues INTEGER DEFAULT 0,              -- 安全问题数
    management_issues INTEGER DEFAULT 0,          -- 管理问题数
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100)
);
```

### 2. projects 表（项目）

```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name VARCHAR(200) NOT NULL,           -- 项目名称
    section VARCHAR(100),                         -- 标段
    contractor VARCHAR(100),                      -- 施工单位
    supervisor VARCHAR(100),                      -- 监理单位
    designer VARCHAR(100),                        -- 设计单位
    builder VARCHAR(100),                         -- 建设单位
    notice_id INTEGER,                            -- 外键：关联通知书
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (notice_id) REFERENCES supervision_notices(id)
);
```

### 3. inspection_points 表（工点）

```sql
CREATE TABLE inspection_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    point_name VARCHAR(200) NOT NULL,             -- 工点名称
    location VARCHAR(200),                        -- 位置
    inspection_date DATE,                         -- 检查时间
    inspector VARCHAR(200),                       -- 检查人员
    project_id INTEGER NOT NULL,                  -- 外键：关联项目
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

### 4. issues 表（问题/隐患）

```sql
CREATE TABLE issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_number VARCHAR(100),                    -- 隐患编号
    description TEXT NOT NULL,                    -- 问题描述
    issue_category VARCHAR(50),                   -- 问题主类别（质量/安全/管理）
    issue_type VARCHAR(100),                      -- 隐患类型（安全子类）
    severity INTEGER DEFAULT 3,                   -- 隐患等级（1-5，默认3）
    rectification_notice VARCHAR(100),            -- 整改通知单号
    rectification_measures TEXT,                  -- 整改措施
    deadline DATE,                                -- 整改期限
    status VARCHAR(50) DEFAULT '未整改',          -- 状态
    completion_date DATE,                         -- 整改完成日期
    completion_status VARCHAR(50),                -- 销号情况
    point_id INTEGER NOT NULL,                    -- 外键：关联工点
    nlp_confidence FLOAT,                         -- NLP 识别置信度
    manual_reviewed BOOLEAN DEFAULT FALSE,        -- 是否人工审核
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (point_id) REFERENCES inspection_points(id)
);
```

### 5. issue_images 表（问题图片）

```sql
CREATE TABLE issue_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_path VARCHAR(500) NOT NULL,             -- 图片路径
    image_hash VARCHAR(64),                       -- 图片哈希
    image_order INTEGER,                          -- 图片顺序
    description VARCHAR(500),                     -- 图片描述
    issue_id INTEGER NOT NULL,                    -- 外键：关联问题
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (issue_id) REFERENCES issues(id)
);
```

### 6. responsibility_units 表（责任单位）

```sql
CREATE TABLE responsibility_units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_id INTEGER NOT NULL,                    -- 外键：关联问题
    unit_type VARCHAR(50),                        -- 单位类型（建设/设计/施工/监理）
    unit_name VARCHAR(100),                       -- 单位名称
    responsible_person VARCHAR(100),              -- 责任人
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (issue_id) REFERENCES issues(id)
);
```

---

## 🏷️ 问题分类体系

### 主类别（3 个）
1. **质量问题** (Quality)
2. **安全问题** (Safety)
3. **管理问题** (Management)

### 安全子类别（7 个）
1. **防洪防汛** (Flood Prevention)
2. **消防安全** (Fire Safety)
3. **隧道安全** (Tunnel Safety)
4. **桥梁安全** (Bridge Safety)
5. **劳动作业安全** (Labor Safety)
6. **交通安全** (Traffic Safety)
7. **营业线安全** (Operating Line Safety)

### 隐患等级（5 级）
- **1 级**：严重
- **2 级**：较重
- **3 级**：一般（默认）
- **4 级**：轻微
- **5 级**：其他

---

## 📥 数据导入流程

### 从 Excel 导入

```
Excel 文件
    ↓
解析 Excel 行数据
    ↓
提取字段值
    ↓
数据验证和清洗
    ↓
映射到数据库表
    ├─ supervision_notices
    ├─ projects
    ├─ inspection_points
    ├─ issues
    ├─ issue_images
    └─ responsibility_units
    ↓
保存到数据库
    ↓
生成导入报告
```

### 从 Word 导入

```
Word 文档
    ↓
提取文本和图片
    ↓
正则表达式提取基础信息
    ├─ 编号、检查时间、检查人员
    ├─ 项目名称、标段、工点
    └─ 问题统计
    ↓
NLP 模型提取关键实体
    ├─ 单位名称
    ├─ 问题类型
    └─ 问题描述
    ↓
人工审核和修正
    ↓
保存到数据库
```

---

## 🔄 数据关系图

```
supervision_notices (通知书)
    ↓ 1:N
projects (项目)
    ↓ 1:N
inspection_points (工点)
    ↓ 1:N
issues (问题)
    ├─ 1:N → issue_images (图片)
    └─ 1:N → responsibility_units (责任单位)
```

---

## 📝 字段映射示例

### Excel → 数据库

| Excel 字段 | 数据库表 | 数据库字段 | 说明 |
|-----------|--------|----------|------|
| 序号 | issues | issue_number | 隐患编号 |
| 检查时间 | supervision_notices | check_date | 检查日期 |
| 检查单位 | supervision_notices | check_unit | 检查机构 |
| 检查人 | supervision_notices | check_personnel | 检查人员 |
| 检查项目 | projects | project_name | 项目名称 |
| 检查工点 | inspection_points | point_name | 工点名称 |
| 隐患问题描述 | issues | description | 问题描述 |
| 隐患类型 | issues | issue_type | 隐患类型 |
| 隐患等级 | issues | severity | 隐患等级 |
| 整改要求 | issues | rectification_measures | 整改措施 |
| 整改期限 | issues | deadline | 整改期限 |
| 整改责任单位 | responsibility_units | unit_type | 单位类型 |
| 整改责任人 | responsibility_units | responsible_person | 责任人 |
| 整改完成日期 | issues | completion_date | 完成日期 |
| 销号情况 | issues | completion_status | 销号状态 |

---

## 🚀 实现优先级

### Phase 1（必须）
- ✅ 创建数据库表结构
- ✅ 实现 Excel 导入功能
- ✅ 实现基础 CRUD 操作
- ✅ 实现数据验证

### Phase 2（重要）
- ⭐ 实现 Word 文档导入
- ⭐ 实现正则表达式提取
- ⭐ 实现人工审核界面

### Phase 3（可选）
- 📋 实现 NLP 模型提取
- 📋 实现自动分类
- 📋 实现数据去重


