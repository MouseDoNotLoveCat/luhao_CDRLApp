# 工程质量安全问题库 - 问题列表加载失败 Bug 修复

## 🔴 问题描述

"工程质量安全问题库"页面中，问题列表无法加载，显示 "No Data"。

## 🔍 问题根源

### 错误信息
```
API Error: "no such column: check_date"
```

### 根本原因
后端 `/api/issues` 端点的 SQL 查询中引用了不存在的字段：
- `check_date` - 不存在于 `issues` 表
- `check_unit` - 不存在于 `issues` 表
- `project_name` - 不存在于 `issues` 表
- `section_name` - 不存在于 `issues` 表

这些字段应该通过 JOIN 从其他表获取。

## ✅ 修复方案

### 修改文件
**文件**: `backend/app/main.py` (第 158-214 行)

### 修复内容

**原始代码问题**：
```python
# ❌ 错误：直接从 issues 表查询不存在的字段
SELECT id, issue_number, description, is_rectification_notice,
       document_section, severity, check_date, check_unit,
       project_name, section_name, site_name, issue_type_level1,
       issue_type_level2
FROM issues
```

**修复后的代码**：
```python
# ✅ 正确：通过 JOIN 获取相关字段
SELECT i.id, i.issue_number, i.description, i.is_rectification_notice,
       i.document_section, i.severity, i.site_name, i.issue_type_level1,
       i.issue_type_level2, i.inspection_date as check_date, 
       i.inspection_unit as check_unit,
       s.section_name, p.project_name,
       sn.check_date as notice_check_date, sn.check_unit as notice_check_unit
FROM issues i
LEFT JOIN sections s ON i.section_id = s.id
LEFT JOIN projects p ON s.project_id = p.id
LEFT JOIN supervision_notices sn ON i.supervision_notice_id = sn.id
```

### 关键改动

1. **字段映射**：
   - `i.inspection_date` → `check_date`
   - `i.inspection_unit` → `check_unit`

2. **JOIN 操作**：
   - LEFT JOIN sections 获取 `section_name`
   - LEFT JOIN projects 获取 `project_name`
   - LEFT JOIN supervision_notices 获取通知书相关信息

3. **保留原有逻辑**：
   - 保留 `is_rectification` 过滤条件
   - 保留分页逻辑（LIMIT 和 OFFSET）

## 🧪 验证结果

### API 测试
```bash
curl "http://localhost:8000/api/issues?limit=1&offset=0"
```

### 返回数据示例
```json
[
    {
        "id": 1336,
        "issue_number": "ISSUE_8_1762505698.429635",
        "description": "环境水检测报告缺少Mg2+含量检测内容...",
        "is_rectification_notice": 0,
        "document_section": "other",
        "severity": 3,
        "site_name": "铁山港跨海特大桥",
        "issue_type_level1": null,
        "issue_type_level2": null,
        "check_date": "2025-07-10",
        "check_unit": "南宁监督站",
        "section_name": null,
        "project_name": "未知项目",
        "notice_check_date": "2025-09-16",
        "notice_check_unit": "未知单位"
    }
]
```

✅ **API 现在正常返回数据**

## 📝 前端调试代码

已在 `frontend/src/pages/IssuesPage.vue` 中添加调试日志：
- 记录获取开始
- 记录获取结果
- 记录错误信息

## 🚀 下一步

1. 在浏览器中打开 http://localhost:3000
2. 点击左侧菜单"工程质量安全问题库"
3. 验证问题列表是否正常加载
4. 打开浏览器 Console (F12) 查看调试日志

---

**修复日期**: 2025-11-08  
**修复状态**: ✅ 完成  
**验证状态**: ✅ API 测试通过

