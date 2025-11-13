# 📊 数据库结构详细设计文档

**版本**: 4.0
**更新时间**: 2025-10-25
**状态**: ✅ 已实现

---

## 🎯 设计原则

1. **层级清晰** - 项目 → 标段 → 问题的三层级结构
2. **关系明确** - 每个层级的一对多关系清晰定义
3. **单位管理** - 在标段级别管理施工、监理、设计单位
4. **问题追踪** - 每个问题直接关联到标段，包含工点名称字段
5. **灵活性** - 工点名称作为问题的属性，支持多个工点和多个问题

---

## 📋 数据模型

### 层级结构

```
项目 (Project)
  ├─ 建设单位 (1个)
  └─ 标段 (多个)
       ├─ 施工单位 (1个)
       ├─ 监理单位 (1个)
       ├─ 设计单位 (1个)
       └─ 问题 (多个)
            ├─ 工点名称 (site_name)
            └─ 来自监督通知书
```

**变更说明**：
- ✅ v4.0 删除了 `inspection_points` 表
- ✅ 在 `issues` 表中添加 `site_name` 字段存储工点名称
- ✅ 问题直接关联到标段，简化了数据模型
- ✅ 保持了灵活性，支持多个工点和多个问题

### 表结构详解

#### 1. 项目表 (projects)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 项目ID |
| project_name | VARCHAR(200) | NOT NULL, UNIQUE | 项目名称 |
| builder_unit | VARCHAR(100) | | 建设单位 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**关键点**：
- project_name 唯一，避免重复
- 每个项目对应1个建设单位

#### 2. 标段表 (sections) - 新增

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 标段ID |
| project_id | INTEGER | NOT NULL, FK | 所属项目 |
| section_code | VARCHAR(100) | NOT NULL | 标段编号（如LWZF-2） |
| section_name | VARCHAR(200) | | 标段名称 |
| contractor_unit | VARCHAR(100) | | 施工单位 |
| supervisor_unit | VARCHAR(100) | | 监理单位 |
| designer_unit | VARCHAR(100) | | 设计单位 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**约束**：
- UNIQUE(project_id, section_code) - 同一项目内标段编号唯一

**关键点**：
- 标段是项目和工点之间的中间层
- 每个标段对应1个施工单位、1个监理单位、1个设计单位

#### 3. 工点表 (inspection_points) - ❌ 已删除 (v4.0)

**删除原因**：
- 工点不需要单独作为外键表
- 工点名称现在直接存储在问题表的 `site_name` 字段中
- 简化了数据模型，提高了灵活性

**迁移说明**：
- 原工点表中的 `point_name` 现在存储在 `issues.site_name`
- 原工点表中的 `section_id` 关系现在直接在 `issues.section_id` 中
- 不再需要创建工点记录，直接在问题中指定工点名称

#### 4. 问题表 (issues) ⭐ 核心表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY | 问题ID |
| issue_number | VARCHAR(100) | NOT NULL, UNIQUE | 问题编号 |
| supervision_notice_id | INTEGER | NOT NULL, FK | 来自哪个监督通知书 |
| section_id | INTEGER | NOT NULL, FK | 属于哪个标段 |
| **site_name** | **VARCHAR(200)** | | **✨ v4.0 新增：工点名称** |
| description | TEXT | NOT NULL | 问题描述 |
| severity | INTEGER | DEFAULT 3 | 严重程度（1-6） |
| issue_category | VARCHAR(50) | | 问题类别（质量/安全/管理） |
| issue_subcategory | VARCHAR(50) | | 问题子类 |
| keywords | VARCHAR(500) | | 关键词 |
| inspection_unit | VARCHAR(100) | | 检查单位 |
| inspection_date | DATE | | 检查日期 |
| inspection_personnel | VARCHAR(500) | | 检查人员 |
| rectification_requirements | TEXT | | 整改要求/措施 |
| rectification_deadline | DATE | | 整改期限 |
| rectification_date | DATE | | 整改完成日期 |
| rectification_status | VARCHAR(50) | | 整改状态 |
| **responsible_unit** | **VARCHAR(100)** | | **✨ v4.0 新增：责任单位** |
| closure_date | DATE | | 销号日期 |
| closure_status | VARCHAR(50) | | 销号状态 |
| closure_personnel | VARCHAR(100) | | 销号人员 |
| is_rectification_notice | BOOLEAN | DEFAULT 0 | 是否下发整改通知单 |
| is_bad_behavior_notice | BOOLEAN | DEFAULT 0 | 是否不良行为通知单 |
| document_section | VARCHAR(50) | | 文档章节（rectification/other） |
| document_source | VARCHAR(50) | | 文档来源（excel/word） |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

**约束**：
- section_id NOT NULL - 每个问题必须关联到标段
- issue_number UNIQUE - 问题编号唯一

**关键点**：
- 问题直接关联到标段（v4.0 变更）
- 工点名称存储在 `site_name` 字段中
- 责任单位存储在 `responsible_unit` 字段中
- 每个问题必须来自一个监督通知书
- is_rectification_notice 标记问题类型
- 字段支持完整的检查、整改、销号流程追踪

---

## 🔗 关系映射

### 一对多关系 (v4.0)

```
projects (1) ──→ (多) sections
sections (1) ──→ (多) issues
supervision_notices (1) ──→ (多) issues
```

**变更说明**：
- ✅ v4.0 移除了 `inspection_points` 中间表
- ✅ 问题现在直接关联到标段
- ✅ 工点信息存储在问题的 `site_name` 字段中

### 查询示例

**查询某项目的所有问题**：
```sql
SELECT i.* FROM issues i
JOIN sections s ON i.section_id = s.id
WHERE s.project_id = ?
```

**查询某标段的所有问题**：
```sql
SELECT i.* FROM issues i
WHERE i.section_id = ?
ORDER BY i.site_name, i.id
```

**查询某工点的所有问题**：
```sql
SELECT i.* FROM issues i
WHERE i.section_id = ? AND i.site_name = ?
```

**查询某标段的所有工点和问题**：
```sql
SELECT s.section_code, ip.point_name, i.issue_number, i.description
FROM sections s
LEFT JOIN inspection_points ip ON s.id = ip.section_id
LEFT JOIN issues i ON ip.id = i.inspection_point_id
WHERE s.id = ?
```

---

## 📊 导入流程

### 导入步骤

1. **解析文件** → 提取项目名、标段、工点、问题信息
2. **创建项目** → 如果项目不存在则创建
3. **创建标段** → 如果标段不存在则创建，关联施工/监理单位
4. **创建工点** → 如果工点不存在则创建
5. **创建问题** → 关联到工点和监督通知书

### 导入数据示例

```
文件：柳梧6号.docx
  ├─ 项目：柳州铁路
  ├─ 标段1：LWZF-2 (中铁上海局 / 北京现代)
  │   └─ 工点：LWZF-2标藤县北站
  │       └─ 问题：南宁站〔2025〕（通知）柳梧6号-R1
  ├─ 标段2：LWXQ (中铁一局 / 中咨管理)
  │   └─ 工点：LWXQ标紫荆瑶山隧道出口
  │       └─ 问题：南宁站〔2025〕（通知）柳梧6号-R2
  └─ ...
```

---

## ✅ 验证规则

1. **项目唯一性** - project_name 唯一
2. **标段唯一性** - (project_id, section_code) 组合唯一
3. **工点唯一性** - (section_id, point_name) 组合唯一
4. **问题必须关联工点** - inspection_point_id NOT NULL
5. **问题编号唯一** - issue_number 唯一

---

## 🔄 迁移说明

从旧结构迁移到新结构的步骤：

1. 创建 sections 表
2. 修改 inspection_points 表，添加 section_id 外键
3. 修改 issues 表，添加 NOT NULL 约束
4. 数据迁移脚本（如需要）


