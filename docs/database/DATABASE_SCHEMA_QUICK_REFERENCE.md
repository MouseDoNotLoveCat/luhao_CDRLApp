# 📚 数据库架构 - 快速参考指南

## 🎯 快速导航

| 需求 | 查看位置 | 说明 |
|------|---------|------|
| 📖 详细文档 | `DATABASE_SCHEMA.md` | 完整的表结构、字段说明、示例 |
| 💻 SQL 注释 | `database_schema.sql` | 每个字段旁边的中文注释 |
| 🔍 元数据查询 | `backend/scripts/create_data_dictionary.sql` | 可选：在数据库中查询字段信息 |
| ⚡ 快速参考 | 本文件 | 常用字段和查询示例 |

---

## 📊 核心表一览

### supervision_notices（监督通知书）
```sql
-- 主要字段
notice_number      -- 通知书编号（唯一）
check_date         -- 检查日期
check_unit         -- 检查单位
check_personnel    -- 检查人员
inspection_basis   -- 检查依据
total_issues_count -- 问题总数
```

### projects（项目）
```sql
-- 主要字段
project_name  -- 项目名称（唯一）
builder_unit  -- 建设单位
```

### sections（标段）
```sql
-- 主要字段
project_id      -- 所属项目 ID（外键）
section_code    -- 标段编号
section_name    -- 标段名称
contractor_unit -- 施工单位
supervisor_unit -- 监理单位
designer_unit   -- 设计单位
```

### issues（隐患问题）
```sql
-- 主要字段
issue_number           -- 问题编号
supervision_notice_id  -- 来自哪个监督通知书（外键）
section_id             -- 属于哪个标段（外键）
site_name              -- 工点名称
issue_category         -- 问题类别（质量/安全/管理）
description            -- 问题描述
severity               -- 严重程度（1-6）
rectification_status   -- 整改状态
closure_status         -- 销号状态
```

---

## 🔗 表关系图

```
projects (1) ──── (N) sections
    ↓
    └──── (N) issues ──── (N) issue_penalties
              ├──── (N) responsibility_units
              └──── (N) issue_images

supervision_notices (1) ──── (N) issues
```

---

## 💡 常用查询示例

### 1. 查询某个监督通知书的所有问题
```sql
SELECT i.* 
FROM issues i
JOIN supervision_notices sn ON i.supervision_notice_id = sn.id
WHERE sn.notice_number = '南宁站[2025]（通知）黄百11号';
```

### 2. 查询某个项目的所有标段
```sql
SELECT * FROM sections 
WHERE project_id = (SELECT id FROM projects WHERE project_name = '黄百铁路');
```

### 3. 查询某个标段的所有问题
```sql
SELECT i.* FROM issues i
WHERE i.section_id = (SELECT id FROM sections WHERE section_code = 'LWZQ-8');
```

### 4. 统计问题数量（按类别）
```sql
SELECT issue_category, COUNT(*) as count
FROM issues
GROUP BY issue_category;
```

### 5. 查询未整改的问题
```sql
SELECT * FROM issues 
WHERE rectification_status IN ('未整改', '整改中', '逾期');
```

### 6. 查询已销号的问题
```sql
SELECT * FROM issues 
WHERE closure_status = '已销号';
```

### 7. 查询下发整改通知单的问题
```sql
SELECT * FROM issues 
WHERE is_rectification_notice = TRUE;
```

### 8. 查询某个监督通知书的统计信息
```sql
SELECT 
  notice_number,
  check_date,
  check_unit,
  quality_issues_count,
  safety_issues_count,
  management_issues_count,
  total_issues_count
FROM supervision_notices
WHERE notice_number = '南宁站[2025]（通知）黄百11号';
```

---

## 📋 字段值参考

### issue_category（问题类别）
- `质量` - 质量问题
- `安全` - 安全问题
- `管理` - 管理问题

### rectification_status（整改状态）
- `未整改` - 未开始整改
- `整改中` - 正在整改
- `已整改` - 已完成整改
- `逾期` - 超过期限未整改

### closure_status（销号状态）
- `未销号` - 未销号
- `已销号` - 已销号

### severity（严重程度）
- `1` - 最严重
- `2` - 很严重
- `3` - 严重
- `4` - 中等
- `5` - 轻微
- `6` - 最轻微

### penalty_type（处罚类型）
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

## 🔑 主要约束

| 表 | 约束 | 说明 |
|----|------|------|
| supervision_notices | UNIQUE(notice_number) | 通知书编号唯一 |
| projects | UNIQUE(project_name) | 项目名称唯一 |
| sections | UNIQUE(project_id, section_code) | 同一项目内标段编号唯一 |
| issues | UNIQUE(issue_number) | 问题编号唯一 |

---

## 📝 数据输入建议

### 监督通知书导入
1. 从 Word 文档自动解析
2. 提取：通知书编号、检查日期、检查单位、检查人员、检查依据
3. 自动统计问题数量

### 问题导入
1. 从 Word 文档自动解析
2. 提取：问题编号、标段、工点、问题描述等
3. 自动分类（质量/安全/管理）

### 整改信息更新
1. 手动输入或导入整改要求、期限
2. 更新整改状态和完成日期
3. 更新销号信息

---

## 🚀 最佳实践

✅ **查询前**
- 确认表名和字段名
- 查看 DATABASE_SCHEMA.md 了解字段含义
- 检查外键关系

✅ **插入数据前**
- 验证外键存在
- 检查唯一性约束
- 确保数据类型匹配

✅ **更新数据时**
- 使用 WHERE 子句精确定位
- 备份重要数据
- 记录修改原因

✅ **删除数据时**
- 注意级联删除（issue_penalties、responsibility_units、issue_images 会被级联删除）
- 确认无其他依赖
- 备份数据

---

## 📞 获取帮助

- 📖 详细文档：查看 `DATABASE_SCHEMA.md`
- 💻 SQL 注释：查看 `database_schema.sql`
- 🔍 元数据查询：执行 `backend/scripts/create_data_dictionary.sql`
- ❓ 问题排查：检查约束和外键关系

---

**最后更新**: 2025-11-05

