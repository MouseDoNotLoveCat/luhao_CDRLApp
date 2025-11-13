# 🗄️ 完整数据库设计方案

## 📋 数据源字段汇总

### 1. Excel 文件字段（建设系统安全隐患库）
```
序号、检查时间、检查单位、检查人、检查项目、检查工点、
隐患问题描述、隐患类型、隐患等级、整改要求（措施）、
整改期限、整改责任单位（建设/设计/施工/监理）、
整改责任人、整改完成日期、销号情况
```

### 2. Word 文件字段（监督检查问题.doc）
```
项目名称、标段名称、工点名称、检查计划时间、
问题类型（1层/2层/3层）、检查单位、问题关键词、
施工单位、设计单位、监理单位、第三方检测单位、
责任单位、问题描述、问题图片/视频、
检查人1/2/3、检查日期、处罚措施、问题类别、
限期整改日期、责任单位负责人、跟踪人员、手机号码、
整改措施内容、整改图片、整改日期
```

### 3. 处罚措施选项（9 个）
```
责令改正、拆除返工、临时停工、
施工一般、施工较大、施工重大、
监理一般、监理较大、监理重大
```

### 4. 问题类别选项（2 个，可多选）
```
签发整改通知单、不良行为通知单
```

---

## 🗄️ 数据库表结构设计

### 表 1: supervision_notices（监督通知书）
```sql
CREATE TABLE supervision_notices (
  id INTEGER PRIMARY KEY,
  notice_number VARCHAR(100) UNIQUE,  -- 通知书编号
  check_date DATE,                     -- 检查日期
  check_unit VARCHAR(100),             -- 检查单位
  check_personnel VARCHAR(500),        -- 检查人员（多人）
  
  -- 统计字段
  quality_issues_count INTEGER DEFAULT 0,
  safety_issues_count INTEGER DEFAULT 0,
  management_issues_count INTEGER DEFAULT 0,
  total_issues_count INTEGER DEFAULT 0,
  
  -- 系统字段
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### 表 2: projects（项目）
```sql
CREATE TABLE projects (
  id INTEGER PRIMARY KEY,
  project_name VARCHAR(200),           -- 项目名称
  section VARCHAR(100),                -- 标段名称
  builder VARCHAR(100),                -- 建设单位
  designer VARCHAR(100),               -- 设计单位
  contractor VARCHAR(100),             -- 施工单位
  supervisor VARCHAR(100),             -- 监理单位
  third_party_tester VARCHAR(100),     -- 第三方检测单位
  
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### 表 3: inspection_points（工点）
```sql
CREATE TABLE inspection_points (
  id INTEGER PRIMARY KEY,
  project_id INTEGER,                  -- 关联项目
  point_name VARCHAR(200),             -- 工点名称
  location VARCHAR(200),               -- 位置
  inspection_date DATE,                -- 检查日期
  inspection_personnel VARCHAR(500),   -- 检查人员
  
  FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

### 表 4: issues（隐患问题）
```sql
CREATE TABLE issues (
  id INTEGER PRIMARY KEY,
  issue_number VARCHAR(100) UNIQUE,    -- 隐患编号
  supervision_notice_id INTEGER,       -- 关联通知书
  inspection_point_id INTEGER,         -- 关联工点

  -- 问题分类
  issue_category VARCHAR(50),          -- 主类别：质量/安全/管理
  issue_subcategory VARCHAR(50),       -- 子类别（安全类）
  issue_type_level1 VARCHAR(100),      -- 问题类型1层
  issue_type_level2 VARCHAR(100),      -- 问题类型2层
  issue_type_level3 VARCHAR(100),      -- 问题类型3层

  -- 问题信息
  description TEXT,                    -- 问题描述
  severity INTEGER DEFAULT 3,          -- 隐患等级（1-6）
  keywords VARCHAR(500),               -- 问题关键词

  -- 整改信息
  rectification_measures TEXT,         -- 整改措施
  deadline DATE,                       -- 整改期限
  completion_date DATE,                -- 整改完成日期
  completion_status VARCHAR(50),       -- 销号情况

  -- 问题类别（可多选）
  is_rectification_notice BOOLEAN,     -- 签发整改通知单 ⭐ 关键字段
  is_bad_behavior_notice BOOLEAN,      -- 不良行为通知单

  -- 文档识别字段
  document_section VARCHAR(50),        -- 文档章节：rectification/other
  document_source VARCHAR(50),         -- 数据来源：excel/word

  -- 系统字段
  created_at TIMESTAMP,
  updated_at TIMESTAMP,

  FOREIGN KEY (supervision_notice_id) REFERENCES supervision_notices(id),
  FOREIGN KEY (inspection_point_id) REFERENCES inspection_points(id)
);
```

### 表 5: issue_penalties（隐患处罚措施）
```sql
CREATE TABLE issue_penalties (
  id INTEGER PRIMARY KEY,
  issue_id INTEGER,                    -- 关联隐患
  penalty_type VARCHAR(50),            -- 处罚措施类型
  
  -- 处罚措施选项：
  -- 责令改正、拆除返工、临时停工、
  -- 施工一般、施工较大、施工重大、
  -- 监理一般、监理较大、监理重大
  
  FOREIGN KEY (issue_id) REFERENCES issues(id)
);
```

### 表 6: responsibility_units（责任单位）
```sql
CREATE TABLE responsibility_units (
  id INTEGER PRIMARY KEY,
  issue_id INTEGER,                    -- 关联隐患
  unit_type VARCHAR(50),               -- 单位类型：建设/设计/施工/监理
  unit_name VARCHAR(200),              -- 单位名称
  responsible_person VARCHAR(100),     -- 责任人
  phone VARCHAR(20),                   -- 手机号码
  
  FOREIGN KEY (issue_id) REFERENCES issues(id)
);
```

### 表 7: issue_images（问题图片）
```sql
CREATE TABLE issue_images (
  id INTEGER PRIMARY KEY,
  issue_id INTEGER,                    -- 关联隐患
  image_type VARCHAR(50),              -- 图片类型：问题/整改
  image_path VARCHAR(500),             -- 图片路径
  image_order INTEGER,                 -- 图片顺序
  description VARCHAR(500),            -- 图片描述
  
  FOREIGN KEY (issue_id) REFERENCES issues(id)
);
```

---

## 📊 数据关系图

```
supervision_notices (1)
    ↓ 1:N
projects (1)
    ↓ 1:N
inspection_points (1)
    ↓ 1:N
issues (1)
    ├─ 1:N → issue_penalties
    ├─ 1:N → responsibility_units
    └─ 1:N → issue_images
```

---

## 🔑 关键字段说明

### 隐患等级（6 级）
- 1 级：重大
- 2 级：突出
- 3 级：一般（默认）
- 4 级：轻微
- 5 级：其他
- 6 级：其他

### 问题分类
- **主类别**：质量、安全、管理
- **安全子类**：防洪防汛、消防安全、隧道安全、桥梁安全、劳动作业安全、交通安全、营业线安全

### 处罚措施（可多选）
- 责令改正
- 拆除返工
- 临时停工
- 施工一般
- 施工较大
- 施工重大
- 监理一般
- 监理较大
- 监理重大

### 问题类别（可多选）
- 签发整改通知单
- 不良行为通知单

---

## 📥 数据导入映射

### Excel → 数据库
| Excel 字段 | 数据库表 | 数据库字段 |
|-----------|--------|----------|
| 序号 | issues | issue_number |
| 检查时间 | supervision_notices | check_date |
| 检查单位 | supervision_notices | check_unit |
| 检查人 | supervision_notices | check_personnel |
| 检查项目 | projects | project_name |
| 检查工点 | inspection_points | point_name |
| 隐患问题描述 | issues | description |
| 隐患类型 | issues | issue_subcategory |
| 隐患等级 | issues | severity |
| 整改要求 | issues | rectification_measures |
| 整改期限 | issues | deadline |
| 整改责任单位 | responsibility_units | unit_type |
| 整改责任人 | responsibility_units | responsible_person |
| 整改完成日期 | issues | completion_date |
| 销号情况 | issues | completion_status |

### Word → 数据库
| Word 字段 | 数据库表 | 数据库字段 |
|----------|--------|----------|
| 项目名称 | projects | project_name |
| 标段名称 | projects | section |
| 工点名称 | inspection_points | point_name |
| 问题类型（1/2/3层） | issues | issue_type_level1/2/3 |
| 施工单位 | responsibility_units | unit_name (type=施工) |
| 设计单位 | responsibility_units | unit_name (type=设计) |
| 监理单位 | responsibility_units | unit_name (type=监理) |
| 问题描述 | issues | description |
| 处罚措施 | issue_penalties | penalty_type |
| 问题类别 | issues | is_rectification_notice/is_bad_behavior_notice |
| 检查人 | supervision_notices | check_personnel |
| 检查日期 | inspection_points | inspection_date |

---

## ✅ 设计特点

1. **完整覆盖** - 包含 Excel 和 Word 的所有字段
2. **灵活扩展** - 支持多选字段（处罚措施、问题类别）
3. **数据完整性** - 完整的关系设计和外键约束
4. **易于查询** - 合理的表结构和索引设计
5. **支持分析** - 统计字段便于数据分析


