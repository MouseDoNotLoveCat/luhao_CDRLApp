# 📥 数据导入规范

## 🎯 导入数据源

### 1. 建设系统安全隐患库 (Excel)
- **文件格式**: .xlsx
- **工作表**: 建设系统（2025）
- **数据行**: 从第 3 行开始（第 1-2 行为表头）
- **优先级**: ⭐⭐⭐ 最高（前期重点）

### 2. 监督通知书 (Word)
- **文件格式**: .docx
- **优先级**: ⭐⭐ 中等（后期实现）

---

## 📋 Excel 导入字段映射

### 表头行（第 1-2 行）

| 列号 | 第1行 | 第2行 | 数据库字段 | 说明 |
|------|-------|-------|----------|------|
| A | 序号 | - | issues.issue_number | 隐患编号 |
| B | 检查时间 | - | supervision_notices.check_date | 检查日期 |
| C | 检查单位 | - | supervision_notices.check_unit | 检查机构 |
| D | 检查人 | - | supervision_notices.check_personnel | 检查人员 |
| E | 检查项目 | - | projects.project_name | 项目名称 |
| F | 检查工点 | - | inspection_points.point_name | 工点名称 |
| G | 隐患问题描述 | - | issues.description | 问题描述 |
| H | 隐患类型 | - | issues.issue_type | 隐患类型 |
| I | 隐患等级 | - | issues.severity | 隐患等级 |
| J | 整改要求（措施） | - | issues.rectification_measures | 整改措施 |
| K | 整改期限 | - | issues.deadline | 整改期限 |
| L | 整改责任单位 | 建设 | responsibility_units.unit_type | 建设单位 |
| M | 整改责任单位 | 设计 | responsibility_units.unit_type | 设计单位 |
| N | 整改责任单位 | 施工 | responsibility_units.unit_type | 施工单位 |
| O | 整改责任单位 | 监理 | responsibility_units.unit_type | 监理单位 |
| P | 整改责任人 | - | responsibility_units.responsible_person | 责任人 |
| Q | 整改完成日期 | - | issues.completion_date | 完成日期 |
| R | 销号情况 | - | issues.completion_status | 销号状态 |

---

## 🔄 导入流程

### 步骤 1：文件验证
```
检查文件格式
  ↓
检查工作表名称
  ↓
检查表头行
  ↓
验证通过 → 继续
验证失败 → 报错
```

### 步骤 2：数据提取
```
逐行读取 Excel 数据（从第 3 行开始）
  ↓
提取每一行的字段值
  ↓
检查必填字段
  ↓
数据验证和清洗
```

### 步骤 3：数据映射
```
提取的数据
  ↓
映射到数据库表
  ├─ supervision_notices
  ├─ projects
  ├─ inspection_points
  ├─ issues
  └─ responsibility_units
  ↓
生成 SQL 语句
```

### 步骤 4：数据保存
```
开始事务
  ↓
执行 SQL 语句
  ↓
提交事务
  ↓
生成导入报告
```

---

## 📝 数据验证规则

### 必填字段
- ✅ 序号 (issue_number)
- ✅ 检查时间 (check_date)
- ✅ 检查单位 (check_unit)
- ✅ 检查人 (check_personnel)
- ✅ 检查项目 (project_name)
- ✅ 检查工点 (point_name)
- ✅ 隐患问题描述 (description)
- ✅ 隐患类型 (issue_type)
- ✅ 隐患等级 (severity)
- ✅ 整改期限 (deadline)

### 可选字段
- ⏳ 整改要求 (rectification_measures)
- ⏳ 整改完成日期 (completion_date)
- ⏳ 销号情况 (completion_status)

### 数据类型验证
| 字段 | 类型 | 验证规则 |
|------|------|--------|
| 检查时间 | Date | YYYY-MM-DD 格式 |
| 隐患等级 | Integer | 1-5 之间 |
| 整改期限 | Date | YYYY-MM-DD 格式 |
| 整改完成日期 | Date | YYYY-MM-DD 格式 |

### 业务规则验证
- ✅ 隐患等级必须在 1-5 之间
- ✅ 整改期限必须晚于检查时间
- ✅ 完成日期必须晚于检查时间
- ✅ 隐患类型必须是有效的安全子类别

---

## 🏷️ 隐患类型映射

### 安全子类别映射表

| 隐患类型（Excel） | 数据库值 | 主类别 |
|-----------------|--------|-------|
| 防洪防汛 | flood_prevention | 安全 |
| 消防安全 | fire_safety | 安全 |
| 隧道安全 | tunnel_safety | 安全 |
| 桥梁安全 | bridge_safety | 安全 |
| 劳动作业安全 | labor_safety | 安全 |
| 交通安全 | traffic_safety | 安全 |
| 营业线安全 | operating_line_safety | 安全 |
| 一般 | general | 安全 |
| 质量问题 | quality | 质量 |
| 管理行为 | management | 管理 |

---

## 📊 导入报告

### 导入成功报告
```
导入统计
├─ 总行数: 100
├─ 成功导入: 98
├─ 失败行数: 2
└─ 成功率: 98%

导入详情
├─ 新增通知书: 5
├─ 新增项目: 8
├─ 新增工点: 15
├─ 新增隐患: 98
└─ 新增责任单位: 120

失败详情
├─ 行 50: 隐患等级无效（值: 10）
└─ 行 75: 检查时间格式错误（值: 2025/01/01）
```

### 导入失败报告
```
导入失败
├─ 原因: 文件格式错误
├─ 详情: 工作表名称不匹配
└─ 建议: 请检查文件是否为正确的 Excel 文件
```

---

## 🔍 数据去重规则

### 通知书去重
- 按 notice_number 去重
- 如果已存在，则更新而不是新增

### 项目去重
- 按 (project_name, section) 组合去重
- 如果已存在，则关联而不是新增

### 工点去重
- 按 (point_name, project_id) 组合去重
- 如果已存在，则关联而不是新增

### 隐患去重
- 按 issue_number 去重
- 如果已存在，则更新而不是新增

---

## 🚀 实现优先级

### Phase 1（必须）
- ✅ 实现 Excel 文件读取
- ✅ 实现表头验证
- ✅ 实现数据提取
- ✅ 实现数据验证
- ✅ 实现数据保存

### Phase 2（重要）
- ⭐ 实现导入报告生成
- ⭐ 实现错误处理和回滚
- ⭐ 实现数据去重

### Phase 3（可选）
- 📋 实现批量导入
- 📋 实现导入历史记录
- 📋 实现导入模板下载

---

## 💡 使用示例

### 导入 Excel 文件

```python
from app.services.import_service import ExcelImportService

# 创建导入服务
service = ExcelImportService()

# 导入文件
result = service.import_excel("path/to/file.xlsx")

# 获取导入结果
print(f"成功导入: {result.success_count}")
print(f"失败行数: {result.failed_count}")
print(f"错误信息: {result.errors}")
```

### 导入结果处理

```python
if result.success:
    # 导入成功
    print("导入完成")
    print(result.report)
else:
    # 导入失败
    print("导入失败")
    for error in result.errors:
        print(f"  - {error}")
```


