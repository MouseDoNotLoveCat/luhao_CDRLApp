# 🚀 快速参考指南 (v4.0)

**版本**: 4.0
**更新时间**: 2025-10-25

---

## 📊 数据库结构速览

### 表关系图 (v4.0)

```
projects (项目)
    ↓ (1对多)
sections (标段)
    ├─ contractor_unit (施工单位)
    ├─ supervisor_unit (监理单位)
    └─ designer_unit (设计单位)
    ↓ (1对多)
issues (问题) ⭐ 直接关联
    ├─ site_name (工点名称)
    ├─ is_rectification_notice (下发整改)
    └─ document_section (文档章节)
```

**v4.0 变更**：
- ✅ 删除了 `inspection_points` 表
- ✅ 工点名称现在存储在 `issues.site_name` 字段

### 8 个表 (v4.0)

| # | 表名 | 说明 | 关键字段 |
|---|------|------|---------|
| 1 | projects | 项目 | project_name, builder_unit |
| 2 | sections | 标段 | section_code, contractor_unit, supervisor_unit, designer_unit |
| 3 | issues | 问题 ⭐ | issue_number, site_name, inspection_date, inspection_personnel, rectification_requirements, rectification_deadline, rectification_status, responsible_unit |
| 4 | supervision_notices | 监督通知书 | notice_number, check_date |
| 5 | issue_penalties | 处罚措施 | penalty_type, issue_id |
| 6 | responsibility_units | 责任单位 | unit_type, unit_name |
| 7 | issue_images | 问题图片 | image_path, issue_id |
| 8 | users | 用户 | username, role |

---

## 🔑 关键概念

### 层级关系 (v4.0)

```
1个项目 = 1个建设单位
1个标段 = 1个施工单位 + 1个监理单位 + 1个设计单位
1个标段 = 多个问题（每个问题包含 site_name 工点名称）
1个问题 = 1个工点（一对一）
```

### 问题分类

- **下发整改通知单** (`is_rectification_notice = 1`)
  - 来自文档第二章
  - 每个工点一个问题
  
- **其它问题** (`is_rectification_notice = 0`)
  - 来自文档第三章
  - 每个工点可能多个问题

---

## ✨ 新增字段说明 (v2.0)

### 问题表 (issues) 新增字段

| 字段名 | 中文表头 | 类型 | 说明 |
|--------|--------|------|------|
| inspection_date | 检查日期 | DATE | 问题被发现的日期 |
| inspection_personnel | 检查人员 | VARCHAR | 参与检查的人员名单 |
| rectification_requirements | 整改要求 | TEXT | 具体的整改措施和要求 |
| rectification_deadline | 整改期限 | DATE | 要求完成整改的截止日期 |
| rectification_date | 整改完成日期 | DATE | 实际完成整改的日期 |
| rectification_status | 整改状态 | VARCHAR | 未整改/整改中/已整改/逾期 |
| closure_date | 销号日期 | DATE | 问题被销号的日期 |
| closure_status | 销号状态 | VARCHAR | 未销号/已销号 |
| closure_personnel | 销号人员 | VARCHAR | 进行销号的人员 |

### 字段映射原则

- **数据库层**：使用英文字段名（snake_case）
- **前端层**：显示中文表头
- **API 层**：支持英文字段名和中文别名

详见：`FIELD_MAPPING_GUIDE.md`

---

## 💾 常用 SQL 查询

### 查询某项目的所有信息

```sql
SELECT 
    p.project_name,
    s.section_code,
    s.contractor_unit,
    s.supervisor_unit,
    ip.point_name,
    i.issue_number,
    i.description,
    i.is_rectification_notice
FROM projects p
LEFT JOIN sections s ON p.id = s.project_id
LEFT JOIN inspection_points ip ON s.id = ip.section_id
LEFT JOIN issues i ON ip.id = i.inspection_point_id
WHERE p.project_name = '柳州铁路'
ORDER BY s.section_code, ip.point_name;
```

### 统计下发整改通知单

```sql
SELECT 
    s.section_code,
    COUNT(*) as count
FROM issues i
JOIN inspection_points ip ON i.inspection_point_id = ip.id
JOIN sections s ON ip.section_id = s.id
WHERE i.is_rectification_notice = 1
GROUP BY s.section_code;
```

### 查询某标段的所有工点

```sql
SELECT 
    ip.point_name,
    COUNT(i.id) as issue_count
FROM inspection_points ip
LEFT JOIN issues i ON ip.id = i.inspection_point_id
WHERE ip.section_id = ?
GROUP BY ip.id;
```

---

## 🔧 常用命令

### 查看数据库

```bash
# 查看所有表
sqlite3 backend/cdrl.db ".tables"

# 查看表结构
sqlite3 backend/cdrl.db ".schema projects"

# 导出为 CSV
sqlite3 backend/cdrl.db ".mode csv" ".output data.csv" "SELECT * FROM issues;" ".output stdout"
```

### 导入文件

```bash
# 导入单个文件
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from backend.app.parsers.word_parser import parse_word_document

result = parse_word_document("Samples/柳梧6号.docx")
print(f"项目: {result['project_name']}")
print(f"下发整改: {len(result['rectification_notices'])}")
print(f"其它问题: {len(result['other_issues'])}")
EOF
```

### 查看导入结果

```bash
python3 view_db.py
```

---

## 📋 导入检查清单

导入前：
- [ ] 文件格式为 .docx
- [ ] 文档包含标准章节结构
- [ ] 标段编号以 LW 开头

导入后：
- [ ] 项目已创建
- [ ] 标段已创建（含施工/监理单位）
- [ ] 工点已创建
- [ ] 问题已关联到工点
- [ ] 下发整改通知单数量正确

---

## 🐛 常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 标段编号为 None | 格式不符 | 检查文档中的标段编号 |
| 工点名称不完整 | 格式不标准 | 检查"的"和"（检查日期"之间的内容 |
| 问题数量不对 | 章节识别错误 | 检查文档的章节标题 |
| 导入失败 | 数据库错误 | 检查 cdrl.db 是否存在 |

---

## 📚 相关文档

- `README.md` - 项目总体说明
- `DATABASE_STRUCTURE_DETAILED.md` - 数据库详细设计
- `IMPORT_GUIDE_V2.md` - 导入指南
- `DATABASE_REDESIGN_SUMMARY.md` - 重新设计总结

---

## 🎯 下一步

1. **导入所有文件** - 使用 import_documents_v2.py 导入 Samples 文件夹中的所有文件
2. **验证数据** - 检查导入的数据是否正确
3. **讨论识别错误** - 根据实际情况调整识别逻辑
4. **开发前端** - 基于新的数据结构开发前端界面


