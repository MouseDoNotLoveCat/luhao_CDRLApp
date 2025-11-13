# 📋 字段映射指南

**版本**: 2.0  
**更新时间**: 2025-10-24  
**说明**: 数据库使用英文字段名，前端显示中文表头

---

## 🎯 设计原则

- **数据库层**：使用英文字段名（snake_case）
- **前端层**：显示中文表头和标签
- **API 层**：支持英文字段名和中文别名

---

## 📊 主要表的字段映射

### 1. 监督通知书表 (supervision_notices)

| 英文字段名 | 中文表头 | 类型 | 说明 |
|-----------|--------|------|------|
| id | ID | INTEGER | 主键 |
| notice_number | 通知书编号 | VARCHAR | 如：南宁站〔2025〕（通知）柳梧6号 |
| check_date | 检查日期 | DATE | 检查的日期 |
| check_unit | 检查单位 | VARCHAR | 进行检查的单位 |
| check_personnel | 检查人员 | VARCHAR | 参与检查的人员名单 |
| quality_issues_count | 质量问题数 | INTEGER | 统计字段 |
| safety_issues_count | 安全问题数 | INTEGER | 统计字段 |
| management_issues_count | 管理问题数 | INTEGER | 统计字段 |
| total_issues_count | 总问题数 | INTEGER | 统计字段 |
| created_at | 创建时间 | TIMESTAMP | 系统字段 |
| updated_at | 更新时间 | TIMESTAMP | 系统字段 |

### 2. 项目表 (projects)

| 英文字段名 | 中文表头 | 类型 | 说明 |
|-----------|--------|------|------|
| id | ID | INTEGER | 主键 |
| project_name | 项目名称 | VARCHAR | 如：柳州铁路 |
| builder_unit | 建设单位 | VARCHAR | 项目的建设单位 |
| created_at | 创建时间 | TIMESTAMP | 系统字段 |
| updated_at | 更新时间 | TIMESTAMP | 系统字段 |

### 3. 标段表 (sections)

| 英文字段名 | 中文表头 | 类型 | 说明 |
|-----------|--------|------|------|
| id | ID | INTEGER | 主键 |
| project_id | 项目ID | INTEGER | 外键 |
| section_code | 标段编号 | VARCHAR | 如：LWZF-2, LWXQ |
| section_name | 标段名称 | VARCHAR | 标段的名称 |
| contractor_unit | 施工单位 | VARCHAR | 该标段的施工单位 |
| supervisor_unit | 监理单位 | VARCHAR | 该标段的监理单位 |
| designer_unit | 设计单位 | VARCHAR | 该标段的设计单位 |
| created_at | 创建时间 | TIMESTAMP | 系统字段 |
| updated_at | 更新时间 | TIMESTAMP | 系统字段 |

### 4. 工点表 (inspection_points)

| 英文字段名 | 中文表头 | 类型 | 说明 |
|-----------|--------|------|------|
| id | ID | INTEGER | 主键 |
| section_id | 标段ID | INTEGER | 外键 |
| point_name | 工点名称 | VARCHAR | 如：LWZF-2标藤县北站 |
| location | 位置信息 | VARCHAR | 如：DK225+2 |
| created_at | 创建时间 | TIMESTAMP | 系统字段 |
| updated_at | 更新时间 | TIMESTAMP | 系统字段 |

### 5. 问题表 (issues) ⭐ 重点

| 英文字段名 | 中文表头 | 类型 | 说明 |
|-----------|--------|------|------|
| id | ID | INTEGER | 主键 |
| issue_number | 问题编号 | VARCHAR | 唯一标识 |
| supervision_notice_id | 通知书ID | INTEGER | 外键 |
| inspection_point_id | 工点ID | INTEGER | 外键 |
| issue_category | 问题类别 | VARCHAR | 质量/安全/管理 |
| issue_subcategory | 问题子类 | VARCHAR | 如：防洪防汛 |
| issue_type_level1 | 问题类型1 | VARCHAR | 第一层分类 |
| issue_type_level2 | 问题类型2 | VARCHAR | 第二层分类 |
| issue_type_level3 | 问题类型3 | VARCHAR | 第三层分类 |
| description | 问题描述 | TEXT | 详细的问题描述 |
| severity | 严重程度 | INTEGER | 1-6 级 |
| keywords | 关键词 | VARCHAR | 问题的关键词 |
| **inspection_date** | **检查日期** | **DATE** | **✨ 新增：检查的日期** |
| **inspection_personnel** | **检查人员** | **VARCHAR** | **✨ 新增：检查人员名单** |
| **rectification_requirements** | **整改要求** | **TEXT** | **✨ 新增：整改措施和要求** |
| **rectification_deadline** | **整改期限** | **DATE** | **✨ 新增：整改的截止日期** |
| **rectification_date** | **整改完成日期** | **DATE** | **✨ 新增：实际整改完成日期** |
| **rectification_status** | **整改状态** | **VARCHAR** | **✨ 新增：未整改/整改中/已整改/逾期** |
| **closure_date** | **销号日期** | **DATE** | **✨ 新增：销号的日期** |
| **closure_status** | **销号状态** | **VARCHAR** | **✨ 新增：未销号/已销号** |
| **closure_personnel** | **销号人员** | **VARCHAR** | **✨ 新增：销号人员** |
| is_rectification_notice | 是否下发整改 | BOOLEAN | 是否下发整改通知单 |
| is_bad_behavior_notice | 是否不良行为 | BOOLEAN | 是否不良行为通知单 |
| document_section | 文档章节 | VARCHAR | rectification/other |
| document_source | 文档来源 | VARCHAR | excel/word |
| created_at | 创建时间 | TIMESTAMP | 系统字段 |
| updated_at | 更新时间 | TIMESTAMP | 系统字段 |

---

## 🔄 前端实现示例

### Vue.js 中的字段映射

```javascript
// 字段映射配置
const fieldMapping = {
  // 问题表字段映射
  issues: {
    issue_number: '问题编号',
    description: '问题描述',
    severity: '严重程度',
    inspection_date: '检查日期',
    inspection_personnel: '检查人员',
    rectification_requirements: '整改要求',
    rectification_deadline: '整改期限',
    rectification_date: '整改完成日期',
    rectification_status: '整改状态',
    closure_date: '销号日期',
    closure_status: '销号状态',
    closure_personnel: '销号人员',
    is_rectification_notice: '是否下发整改',
  }
};

// 在表格中使用
const columns = [
  { prop: 'issue_number', label: fieldMapping.issues.issue_number },
  { prop: 'description', label: fieldMapping.issues.description },
  { prop: 'inspection_date', label: fieldMapping.issues.inspection_date },
  { prop: 'rectification_status', label: fieldMapping.issues.rectification_status },
  // ...
];
```

### API 响应示例

```json
{
  "id": 1,
  "issue_number": "南宁站〔2025〕（通知）柳梧6号-R1",
  "description": "现场存放待安装的幕墙MJ-1锚筋长度为10cm，不符合设计长度要求",
  "inspection_date": "2025-05-21",
  "inspection_personnel": "张三, 李四",
  "rectification_requirements": "立即更换符合设计要求的锚筋",
  "rectification_deadline": "2025-05-24",
  "rectification_date": "2025-05-23",
  "rectification_status": "已整改",
  "closure_date": "2025-05-25",
  "closure_status": "已销号",
  "closure_personnel": "王五",
  "severity": 2,
  "is_rectification_notice": true
}
```

---

## 📝 数据库查询示例

### 查询问题的完整信息

```sql
SELECT 
  issue_number AS '问题编号',
  description AS '问题描述',
  inspection_date AS '检查日期',
  inspection_personnel AS '检查人员',
  rectification_requirements AS '整改要求',
  rectification_deadline AS '整改期限',
  rectification_date AS '整改完成日期',
  rectification_status AS '整改状态',
  closure_date AS '销号日期',
  closure_status AS '销号状态',
  closure_personnel AS '销号人员'
FROM issues
WHERE issue_number = ?;
```

### 统计整改进度

```sql
SELECT 
  rectification_status AS '整改状态',
  COUNT(*) AS '数量'
FROM issues
GROUP BY rectification_status;
```

---

## ✅ 新增字段说明

### 检查信息字段

- **inspection_date** - 检查日期：问题被发现的日期
- **inspection_personnel** - 检查人员：参与检查的人员名单

### 整改信息字段

- **rectification_requirements** - 整改要求：具体的整改措施和要求
- **rectification_deadline** - 整改期限：要求完成整改的截止日期
- **rectification_date** - 整改完成日期：实际完成整改的日期
- **rectification_status** - 整改状态：
  - 未整改：尚未开始整改
  - 整改中：正在进行整改
  - 已整改：已完成整改
  - 逾期：超过期限仍未完成

### 销号信息字段

- **closure_date** - 销号日期：问题被销号的日期
- **closure_status** - 销号状态：
  - 未销号：尚未销号
  - 已销号：已完成销号
- **closure_personnel** - 销号人员：进行销号的人员


