# 📋 详细字段映射文档

## 📊 Excel 文件字段映射

### 建设系统安全隐患库（建设部8.7).xlsx

| 序号 | Excel 字段 | 数据库表 | 数据库字段 | 类型 | 说明 |
|------|-----------|--------|----------|------|------|
| 1 | 序号 | issues | issue_number | String | 隐患编号 |
| 2 | 检查时间 | supervision_notices | check_date | Date | 检查日期 |
| 3 | 检查单位 | supervision_notices | check_unit | String | 检查机构 |
| 4 | 检查人 | supervision_notices | check_personnel | String | 检查人员（多人） |
| 5 | 检查项目 | projects | project_name | String | 项目名称 |
| 6 | 检查工点 | inspection_points | point_name | String | 工点名称 |
| 7 | 隐患问题描述 | issues | description | Text | 问题详细描述 |
| 8 | 隐患类型 | issues | issue_subcategory | String | 隐患分类（安全子类） |
| 9 | 隐患等级 | issues | severity | Integer | 隐患等级（1-6） |
| 10 | 整改要求（措施） | issues | rectification_measures | Text | 整改措施 |
| 11 | 整改期限 | issues | deadline | Date | 整改截止日期 |
| 12 | 整改责任单位-建设 | responsibility_units | unit_name | String | 建设单位名称 |
| 13 | 整改责任单位-设计 | responsibility_units | unit_name | String | 设计单位名称 |
| 14 | 整改责任单位-施工 | responsibility_units | unit_name | String | 施工单位名称 |
| 15 | 整改责任单位-监理 | responsibility_units | unit_name | String | 监理单位名称 |
| 16 | 整改责任人 | responsibility_units | responsible_person | String | 责任人姓名 |
| 17 | 整改完成日期 | issues | completion_date | Date | 实际完成日期 |
| 18 | 销号情况 | issues | completion_status | String | 已整改/整改完成等 |

---

## 📄 Word 文件字段映射

### 监督检查问题.doc

| 序号 | Word 字段 | 数据库表 | 数据库字段 | 类型 | 说明 |
|------|----------|--------|----------|------|------|
| 1 | 项目名称 | projects | project_name | String | 项目名称 |
| 2 | 标段名称 | projects | section | String | 标段名称 |
| 3 | 工点名称 | inspection_points | point_name | String | 工点名称 |
| 4 | 检查计划时间 | inspection_points | inspection_date | Date | 检查日期 |
| 5 | 问题类型（1层） | issues | issue_type_level1 | String | 问题类型第1层 |
| 6 | 问题类型（2层） | issues | issue_type_level2 | String | 问题类型第2层 |
| 7 | 问题类型（3层） | issues | issue_type_level3 | String | 问题类型第3层 |
| 8 | 检查单位 | supervision_notices | check_unit | String | 检查单位 |
| 9 | 问题关键词 | issues | keywords | String | 问题关键词 |
| 10 | 施工单位 | responsibility_units | unit_name | String | 施工单位（type=施工） |
| 11 | 设计单位 | responsibility_units | unit_name | String | 设计单位（type=设计） |
| 12 | 监理单位 | responsibility_units | unit_name | String | 监理单位（type=监理） |
| 13 | 第三方检测单位 | projects | third_party_tester | String | 第三方检测单位 |
| 14 | 责任单位 | responsibility_units | unit_name | String | 主要责任单位 |
| 15 | 问题描述 | issues | description | Text | 问题详细描述 |
| 16 | 问题图片或视频 | issue_images | image_path | String | 问题图片路径 |
| 17 | 检查人1/2/3 | supervision_notices | check_personnel | String | 检查人员（多人） |
| 18 | 检查日期 | inspection_points | inspection_date | Date | 检查日期 |
| 19 | 处罚措施 | issue_penalties | penalty_type | String | 处罚措施（多选） |
| 20 | 问题类别 | issues | is_rectification_notice / is_bad_behavior_notice | Boolean | 问题类别（多选） |
| 21 | 限期整改日期 | issues | deadline | Date | 整改期限 |
| 22 | 责任单位负责人 | responsibility_units | responsible_person | String | 责任人 |
| 23 | 跟踪人员 | supervision_notices | check_personnel | String | 跟踪人员 |
| 24 | 手机号码 | responsibility_units | phone | String | 手机号码 |
| 25 | 整改措施内容 | issues | rectification_measures | Text | 整改措施 |
| 26 | 整改图片 | issue_images | image_path | String | 整改图片路径 |
| 27 | 整改日期 | issues | completion_date | Date | 整改完成日期 |

---

## 🔄 多选字段处理

### 处罚措施（issue_penalties 表）

一条隐患记录可以有多个处罚措施，存储在 `issue_penalties` 表中：

| 处罚措施 | 值 | 说明 |
|--------|-----|------|
| 责令改正 | rectification_order | 责令改正 |
| 拆除返工 | demolition_rework | 拆除返工 |
| 临时停工 | temporary_suspension | 临时停工 |
| 施工一般 | construction_general | 施工单位一般处罚 |
| 施工较大 | construction_major | 施工单位较大处罚 |
| 施工重大 | construction_severe | 施工单位重大处罚 |
| 监理一般 | supervision_general | 监理单位一般处罚 |
| 监理较大 | supervision_major | 监理单位较大处罚 |
| 监理重大 | supervision_severe | 监理单位重大处罚 |

**存储方式**：
```sql
-- 一条隐患可以有多条处罚措施记录
INSERT INTO issue_penalties (issue_id, penalty_type) VALUES
  (1, 'rectification_order'),
  (1, 'construction_general');
```

### 问题类别（issues 表）

一条隐患记录可以属于多个问题类别，使用两个布尔字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| is_rectification_notice | Boolean | 是否签发整改通知单 |
| is_bad_behavior_notice | Boolean | 是否不良行为通知单 |

**存储方式**：
```sql
-- 一条隐患可以同时属于两个类别
UPDATE issues SET 
  is_rectification_notice = true,
  is_bad_behavior_notice = true
WHERE id = 1;
```

---

## 📊 数据关系示例

### 示例 1：Excel 导入

```
Excel 行数据：
  序号: 1
  检查时间: 2025-01-03
  检查单位: 沿海建指
  检查人: 童海涛、石鹏飞
  检查项目: QFSG1标段
  检查工点: 皇马隧道LDK109+740-830明挖段
  隐患问题描述: 管棚导向墙未做两侧基础下预埋的钢管桩...
  隐患类型: 一般
  隐患等级: 3
  整改要求: 限期整改，上述问题要求施工单位于1月10日前完成整改...
  整改期限: 2025-01-10
  整改责任单位-施工: 中铁三局钦防增建二线项目部
  整改责任人: 许文涛
  整改完成日期: 2025-01-10
  销号情况: 已整改

映射到数据库：
  supervision_notices:
    - notice_number: auto-generated
    - check_date: 2025-01-03
    - check_unit: 沿海建指
    - check_personnel: 童海涛、石鹏飞
  
  projects:
    - project_name: QFSG1标段
  
  inspection_points:
    - point_name: 皇马隧道LDK109+740-830明挖段
    - inspection_date: 2025-01-03
  
  issues:
    - issue_number: 1
    - description: 管棚导向墙未做两侧基础下预埋的钢管桩...
    - issue_subcategory: 一般
    - severity: 3
    - rectification_measures: 限期整改，上述问题要求施工单位于1月10日前完成整改...
    - deadline: 2025-01-10
    - completion_date: 2025-01-10
    - completion_status: 已整改
  
  responsibility_units:
    - unit_type: 施工
    - unit_name: 中铁三局钦防增建二线项目部
    - responsible_person: 许文涛
```

### 示例 2：Word 导入（多选字段）

```
Word 数据：
  项目名称: 新建柳州至广州铁路柳州至梧州段
  标段名称: LWZQ-1标
  工点名称: DK4+300～+800段路基
  问题类型（1层）: 工程质量
  问题类型（2层）: 路基工程
  问题类型（3层）: 填筑
  处罚措施: 责令改正、施工一般
  问题类别: 签发整改通知单、不良行为通知单

映射到数据库：
  issues:
    - issue_type_level1: 工程质量
    - issue_type_level2: 路基工程
    - issue_type_level3: 填筑
    - is_rectification_notice: true
    - is_bad_behavior_notice: true
  
  issue_penalties:
    - penalty_type: rectification_order
    - penalty_type: construction_general
```

---

## ✅ 数据验证规则

### 必填字段
- ✅ issue_number (隐患编号)
- ✅ check_date (检查日期)
- ✅ check_unit (检查单位)
- ✅ project_name (项目名称)
- ✅ point_name (工点名称)
- ✅ description (问题描述)
- ✅ severity (隐患等级)

### 数据类型验证
- 日期字段：YYYY-MM-DD 格式
- 等级字段：1-6 之间的整数
- 多选字段：逗号分隔或多条记录

### 业务规则验证
- ✅ 隐患等级必须在 1-6 之间
- ✅ 整改期限必须晚于检查时间
- ✅ 完成日期必须晚于检查时间
- ✅ 处罚措施必须是有效的选项
- ✅ 问题类别至少选择一个


