# 📊 CDRL 数据库架构文档

## 概述

工程隐患库管理应用 (CDRL - Constructor Defect & Risk Library) 的数据库架构设计文档。

**数据库类型**: SQLite  
**版本**: 1.0  
**最后更新**: 2025-11-05

---

## 📋 表结构说明

### 1. supervision_notices（监督通知书）

存储监督通知书的基本信息。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PK, AI | 主键 |
| notice_number | VARCHAR(100) | UNIQUE, NOT NULL | 通知书编号（如：南宁站[2025]（通知）黄百11号） |
| check_date | DATE | NOT NULL | 检查日期 |
| check_unit | VARCHAR(100) | NOT NULL | 检查单位（如：南宁监督站） |
| check_personnel | VARCHAR(500) | NULL | 检查人员（人名列表，用、分隔） |
| inspection_basis | TEXT | NULL | 检查依据（文件名称和文号） |
| quality_issues_count | INTEGER | DEFAULT 0 | 质量问题数 |
| safety_issues_count | INTEGER | DEFAULT 0 | 安全问题数 |
| management_issues_count | INTEGER | DEFAULT 0 | 管理问题数 |
| total_issues_count | INTEGER | DEFAULT 0 | 问题总数 |
| created_at | TIMESTAMP | DEFAULT NOW | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW | 更新时间 |

**示例**:
```
notice_number: 南宁站[2025]（通知）黄百11号
check_date: 2025-09-09
check_unit: 南宁监督站
check_personnel: 卢浩、陈胜及建设部第四检查组胡云龙
inspection_basis: 根据《国铁集团关于开展在建铁路桥梁施工安全隐患排查整治的紧急通知》...
```

---

### 2. projects（项目）

存储铁路项目的基本信息。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PK, AI | 主键 |
| project_name | VARCHAR(200) | UNIQUE, NOT NULL | 项目名称（如：黄百铁路、柳梧铁路） |
| builder_unit | VARCHAR(100) | NULL | 建设单位（1个项目对应1个建设单位） |
| created_at | TIMESTAMP | DEFAULT NOW | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW | 更新时间 |

---

### 3. sections（标段）

存储项目下的标段信息。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INTEGER | PK, AI | 主键 |
| project_id | INTEGER | FK, NOT NULL | 所属项目 ID |
| section_code | VARCHAR(100) | NOT NULL | 标段编号（如：LWZF-2、LWXQ、LWZQ-8） |
| section_name | VARCHAR(200) | NULL | 标段名称（如：太平隧道出口） |
| contractor_unit | VARCHAR(100) | NULL | 施工单位（1个标段对应1个施工单位） |
| supervisor_unit | VARCHAR(100) | NULL | 监理单位（1个标段对应1个监理单位） |
| designer_unit | VARCHAR(100) | NULL | 设计单位（1个标段对应1个设计单位） |
| created_at | TIMESTAMP | DEFAULT NOW | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT NOW | 更新时间 |

**约束**: UNIQUE(project_id, section_code)

---

### 4. issues（隐患问题）

存储检查发现的隐患问题。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键 |
| issue_number | VARCHAR(100) | 问题编号（如：(1)、(2)等） |
| supervision_notice_id | INTEGER | 来自哪个监督通知书 |
| section_id | INTEGER | 属于哪个标段 |
| site_name | VARCHAR(200) | 工点名称（如"藤县北站"、"紫荆瑶山隧道出口"） |
| issue_category | VARCHAR(50) | 问题类别（质量/安全/管理） |
| issue_subcategory | VARCHAR(50) | 安全子类（防洪防汛、消防安全等） |
| description | TEXT | 问题描述 |
| severity | INTEGER | 严重程度（1-6，1最严重） |
| keywords | VARCHAR(500) | 关键词（用于搜索和分类） |
| inspection_unit | VARCHAR(100) | 检查单位 |
| inspection_date | DATE | 检查日期 |
| inspection_personnel | VARCHAR(500) | 检查人员 |
| rectification_requirements | TEXT | 整改要求（措施） |
| rectification_deadline | DATE | 整改期限 |
| rectification_date | DATE | 整改完成日期 |
| rectification_status | VARCHAR(50) | 整改状态（未整改/整改中/已整改/逾期） |
| closure_date | DATE | 销号日期 |
| closure_status | VARCHAR(50) | 销号状态（未销号/已销号） |
| closure_personnel | VARCHAR(100) | 销号人员 |
| is_rectification_notice | BOOLEAN | 是否下发整改通知单 |
| is_bad_behavior_notice | BOOLEAN | 是否不良行为通知单 |
| responsible_unit | VARCHAR(100) | 责任单位（施工单位/监理单位等） |
| document_section | VARCHAR(50) | 文档章节（'rectification' 或 'other'） |
| document_source | VARCHAR(50) | 文档来源（'excel' 或 'word'） |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

### 5. issue_penalties（隐患处罚措施）

存储问题的处罚措施（支持多选）。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键 |
| issue_id | INTEGER | 所属问题 ID |
| penalty_type | VARCHAR(50) | 处罚类型 |
| created_at | TIMESTAMP | 创建时间 |

**penalty_type 可选值**:
- `rectification_order` - 责令改正
- `demolition_rework` - 拆除返工
- `temporary_suspension` - 临时停工
- `construction_general` - 施工一般
- `construction_major` - 施工较大
- `construction_severe` - 施工重大
- `supervision_general` - 监理一般
- `supervision_major` - 监理较大
- `supervision_severe` - 监理重大

---

### 6. responsibility_units（责任单位）

存储问题的具体责任单位和责任人。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键 |
| issue_id | INTEGER | 所属问题 ID |
| unit_type | VARCHAR(50) | 单位类型（建设/设计/施工/监理） |
| unit_name | VARCHAR(200) | 单位名称 |
| responsible_person | VARCHAR(100) | 责任人姓名 |
| phone | VARCHAR(20) | 联系电话 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

### 7. issue_images（问题图片）

存储问题相关的图片信息。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键 |
| issue_id | INTEGER | 所属问题 ID |
| image_type | VARCHAR(50) | 图片类型（问题/整改） |
| image_path | VARCHAR(500) | 图片路径 |
| image_order | INTEGER | 图片顺序 |
| description | VARCHAR(500) | 图片描述 |
| created_at | TIMESTAMP | 创建时间 |

---

## 📊 视图说明

### v_issues_summary（隐患统计视图）
按监督通知书统计问题数量，分类显示质量、安全、管理问题。

### v_rectification_progress（整改进度视图）
显示问题的整改进度，包括是否按期完成。

### v_rectification_notices_summary（下发整改通知单统计视图）
统计每个监督通知书中下发整改通知单的问题数和其他问题数。

### v_issues_by_type（问题分类视图）
按问题类型和严重程度分类显示问题。

---

## 🔑 关键关系

```
projects (1) ──── (N) sections
    ↓
    └──── (N) issues ──── (N) issue_penalties
              ├──── (N) responsibility_units
              └──── (N) issue_images

supervision_notices (1) ──── (N) issues
```

---

## 📝 使用建议

1. **查询问题统计**: 使用 `v_issues_summary` 视图
2. **查询整改进度**: 使用 `v_rectification_progress` 视图
3. **查询下发整改通知单**: 使用 `v_rectification_notices_summary` 视图
4. **查询问题分类**: 使用 `v_issues_by_type` 视图

---

## 🔄 数据流向

1. **导入阶段**: Word 文档 → 解析器 → supervision_notices + issues
2. **处理阶段**: 更新 issues 的整改信息、销号信息等
3. **查询阶段**: 通过视图查询统计数据

---

## 📌 注意事项

- SQLite 不支持字段级别的 COMMENT，本文档作为数据字典补充说明
- 所有时间戳字段使用 TIMESTAMP 类型，默认为当前时间
- 外键约束已启用，删除问题时会级联删除相关的处罚措施、责任单位、图片等
- 建议定期备份数据库文件

