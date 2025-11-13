# 🗄️ 数据库结构更新总结

## 📋 更新内容

### 1. 隐患等级调整
- **之前**：5 级（1-5）
- **现在**：6 级（1-6）
- **原因**：根据实际需求，添加了第 6 级"其他"

### 2. 新增表：隐患处罚措施 (issue_penalties)
- **用途**：存储隐患的处罚措施（支持多选）
- **字段**：
  - id (主键)
  - issue_id (外键，关联隐患)
  - penalty_type (处罚措施类型)
  - created_at (创建时间)

### 3. 新增字段：问题类别（issues 表）
- **字段 1**：is_rectification_notice (Boolean) - 签发整改通知单
- **字段 2**：is_bad_behavior_notice (Boolean) - 不良行为通知单
- **用途**：支持一条隐患同时属于多个问题类别

### 4. 新增字段：处罚措施选项
支持 9 个处罚措施选项：
1. 责令改正 (rectification_order)
2. 拆除返工 (demolition_rework)
3. 临时停工 (temporary_suspension)
4. 施工一般 (construction_general)
5. 施工较大 (construction_major)
6. 施工重大 (construction_severe)
7. 监理一般 (supervision_general)
8. 监理较大 (supervision_major)
9. 监理重大 (supervision_severe)

### 5. 新增字段：第三方检测单位
- **表**：projects
- **字段**：third_party_tester (VARCHAR(100))
- **用途**：存储第三方检测单位信息

### 6. 新增字段：问题关键词
- **表**：issues
- **字段**：keywords (VARCHAR(500))
- **用途**：存储问题关键词，便于搜索

### 7. 新增字段：问题类型 3 层分类
- **表**：issues
- **字段**：
  - issue_type_level1 (VARCHAR(100)) - 第 1 层
  - issue_type_level2 (VARCHAR(100)) - 第 2 层
  - issue_type_level3 (VARCHAR(100)) - 第 3 层
- **用途**：支持详细的问题分类

### 8. 新增字段：图片类型
- **表**：issue_images
- **字段**：image_type (VARCHAR(50)) - 问题/整改
- **用途**：区分问题图片和整改图片

### 9. 新增字段：手机号码
- **表**：responsibility_units
- **字段**：phone (VARCHAR(20))
- **用途**：存储责任人的手机号码

---

## 📊 完整的表结构

### 表 1: supervision_notices（监督通知书）
```
id, notice_number, check_date, check_unit, check_personnel,
quality_issues_count, safety_issues_count, management_issues_count, total_issues_count,
created_at, updated_at
```

### 表 2: projects（项目）
```
id, project_name, section, builder, designer, contractor, supervisor, third_party_tester,
created_at, updated_at
```

### 表 3: inspection_points（工点）
```
id, project_id, point_name, location, inspection_date, inspection_personnel,
created_at, updated_at
```

### 表 4: issues（隐患问题）
```
id, issue_number, supervision_notice_id, inspection_point_id,
issue_category, issue_subcategory, issue_type_level1, issue_type_level2, issue_type_level3,
description, severity, keywords,
rectification_measures, deadline, completion_date, completion_status,
is_rectification_notice, is_bad_behavior_notice,
created_at, updated_at
```

### 表 5: issue_penalties（隐患处罚措施）- 新增
```
id, issue_id, penalty_type, created_at
```

### 表 6: responsibility_units（责任单位）
```
id, issue_id, unit_type, unit_name, responsible_person, phone,
created_at, updated_at
```

### 表 7: issue_images（问题图片）
```
id, issue_id, image_type, image_path, image_order, description, created_at
```

---

## 🔄 数据导入映射更新

### Excel 导入
- ✅ 所有 18 个字段都已映射
- ✅ 支持多个责任单位（建设/设计/施工/监理）
- ✅ 支持多个检查人员

### Word 导入
- ✅ 所有 27 个字段都已映射
- ✅ 支持 3 层问题分类
- ✅ 支持多个处罚措施
- ✅ 支持多个问题类别
- ✅ 支持多个检查人员

---

## 📝 文件更新

### 已更新的文件
1. **README.md** - 更新了数据库结构部分
2. **DATABASE_SCHEMA_COMPLETE.md** - 新建，完整的数据库设计
3. **FIELD_MAPPING_DETAILED.md** - 新建，详细的字段映射
4. **database_schema.sql** - 新建，SQL 初始化脚本

### 新建的文件
- DATABASE_SCHEMA_COMPLETE.md - 完整数据库设计方案
- FIELD_MAPPING_DETAILED.md - 详细字段映射文档
- database_schema.sql - SQL 初始化脚本
- DATABASE_UPDATE_SUMMARY.md - 本文件

---

## 🚀 下一步行动

### 1. 数据库初始化
```bash
# 使用 SQLite
sqlite3 cdrl.db < database_schema.sql

# 或使用 Python
python -c "
import sqlite3
conn = sqlite3.connect('cdrl.db')
with open('database_schema.sql', 'r') as f:
    conn.executescript(f.read())
conn.close()
"
```

### 2. 验证表结构
```bash
sqlite3 cdrl.db ".tables"
sqlite3 cdrl.db ".schema issues"
```

### 3. 实现数据导入
- 实现 Excel 导入功能
- 实现 Word 导入功能
- 实现数据验证和清洗

### 4. 实现数据管理
- 实现 CRUD 操作
- 实现数据查询和搜索
- 实现数据统计分析

---

## ✅ 设计特点

### 1. 完整覆盖
- ✅ Excel 文件的所有 18 个字段
- ✅ Word 文件的所有 27 个字段
- ✅ 支持多选字段（处罚措施、问题类别）

### 2. 灵活扩展
- ✅ 支持 3 层问题分类
- ✅ 支持多个责任单位
- ✅ 支持多个检查人员
- ✅ 支持多个处罚措施

### 3. 数据完整性
- ✅ 完整的外键约束
- ✅ 合理的索引设计
- ✅ 统计字段便于分析

### 4. 易于维护
- ✅ 清晰的表结构
- ✅ 详细的字段说明
- ✅ 完整的 SQL 脚本

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
    ├─ 1:N → issue_penalties (处罚措施)
    ├─ 1:N → responsibility_units (责任单位)
    └─ 1:N → issue_images (问题图片)
```

---

## 🎯 关键改进

| 方面 | 改进 |
|------|------|
| **字段覆盖** | 从 15 个字段扩展到 27+ 个字段 |
| **多选支持** | 新增处罚措施和问题类别的多选支持 |
| **分类体系** | 支持 3 层问题分类 |
| **数据完整性** | 完整的外键约束和索引 |
| **易用性** | 提供完整的 SQL 初始化脚本 |

---

**更新日期**：2025-10-24

**版本**：2.0

**状态**：✅ 完成


