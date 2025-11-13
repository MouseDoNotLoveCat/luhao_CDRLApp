# 📥 文档导入指南 (v2.0)

**版本**: 2.0  
**更新时间**: 2025-10-24  
**状态**: ✅ 已实现

---

## 🎯 导入流程概述

```
Word 文档
  ↓
解析文件 (word_parser.py)
  ├─ 提取项目名称
  ├─ 识别标段编号、施工单位、监理单位
  ├─ 识别工点名称
  ├─ 识别下发整改通知单的问题
  └─ 识别其它问题
  ↓
导入数据库 (import_documents_v2.py)
  ├─ 创建/获取项目
  ├─ 创建/获取标段
  ├─ 创建/获取工点
  └─ 创建问题记录
  ↓
数据库存储
```

---

## 📄 文档格式要求

### 监督通知书标准格式

```
[文档标题]
南宁站[2025]（通知）柳梧6号

[第一章：基本信息]
检查日期：2025-05-20
检查单位：...

[第二章：下发整改通知单的工点及问题]
（一）由中铁上海局施工、北京现代监理的LWZF-2标藤县北站（检查日期：2025-05-21）
检查情况：...
处理措施：...

（二）由中铁一局施工、中咨管理监理的LWXQ标紫荆瑶山隧道出口（检查日期：...）
...

[第三章：其他主要质量安全问题]
（一）单位名称
1. 工点名称
（1）具体问题描述
（2）具体问题描述
...
```

### 关键信息提取规则

| 信息 | 格式 | 示例 |
|------|------|------|
| **标段编号** | LW[A-Z]+(-?\d+)? | LWZF-2, LWXQ, LWZQ-8 |
| **施工单位** | 由...施工 | 由中铁上海局施工 |
| **监理单位** | 、...监理 | 、北京现代监理 |
| **工点名称** | 的...（检查日期 | 的LWZF-2标藤县北站（检查日期 |
| **下发整改** | （一）、（二）等 | 汉字序号 |
| **其它问题** | （1）、（2）等 | 数字序号 |

---

## 🚀 快速导入

### 方法1：Python 脚本导入

```bash
cd /path/to/CDRLApp

# 导入单个文件
python3 << 'EOF'
import sys
sys.path.insert(0, '.')

from backend.app.parsers.word_parser import parse_word_document
import sqlite3

# 解析文件
result = parse_word_document("Samples/柳梧6号.docx")

# 导入数据库
conn = sqlite3.connect("backend/cdrl.db")
cursor = conn.cursor()

# ... 导入逻辑 ...

conn.close()
EOF
```

### 方法2：使用导入脚本

```bash
python backend/scripts/import_documents_v2.py
```

---

## 📊 导入结果验证

### 查看导入结果

```bash
python3 << 'EOF'
import sqlite3

conn = sqlite3.connect("backend/cdrl.db")
cursor = conn.cursor()

# 查看项目
print("项目：")
cursor.execute("SELECT id, project_name FROM projects")
for row in cursor.fetchall():
    print(f"  {row[1]}")

# 查看标段
print("\n标段：")
cursor.execute("""
    SELECT s.section_code, s.contractor_unit, s.supervisor_unit
    FROM sections s
""")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} / {row[2]}")

# 查看工点
print("\n工点：")
cursor.execute("""
    SELECT ip.point_name, s.section_code
    FROM inspection_points ip
    JOIN sections s ON ip.section_id = s.id
""")
for row in cursor.fetchall():
    print(f"  {row[0]} ({row[1]})")

# 查看问题
print("\n问题：")
cursor.execute("""
    SELECT i.issue_number, i.is_rectification_notice, ip.point_name
    FROM issues i
    JOIN inspection_points ip ON i.inspection_point_id = ip.id
""")
for row in cursor.fetchall():
    status = "✅ 下发整改" if row[1] else "❌ 其它问题"
    print(f"  {status}: {row[0]} -> {row[2]}")

conn.close()
EOF
```

---

## 🔍 常见问题

### Q1: 标段编号识别失败

**症状**：标段编号为 None

**原因**：标段编号格式不符合预期

**解决**：检查文档中的标段编号格式，确保以 LW 开头

### Q2: 工点名称识别不完整

**症状**：工点名称只有部分内容

**原因**：工点名称中包含特殊字符或格式不标准

**解决**：检查文档格式，确保工点名称在"的"和"（检查日期"之间

### Q3: 问题数量不对

**症状**：导入的问题数量与文档不符

**原因**：可能是下发整改通知单和其它问题的识别有误

**解决**：检查文档中的章节标题是否标准

---

## 📝 导入脚本说明

### backend/scripts/import_documents_v2.py

**功能**：按照新的数据库结构导入文档

**主要步骤**：

1. 解析 Word 文件
2. 创建/获取项目
3. 创建/获取标段
4. 创建/获取工点
5. 创建问题记录

**使用方式**：

```python
from backend.scripts.import_documents_v2 import import_document

import_document("backend/cdrl.db", "Samples/柳梧6号.docx")
```

---

## 🔄 批量导入

### 导入所有文件

```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '.')

from pathlib import Path
from backend.app.parsers.word_parser import parse_word_document
import sqlite3

samples_dir = Path("Samples")
db_path = "backend/cdrl.db"

for file_path in samples_dir.glob("*.docx"):
    print(f"\n导入: {file_path.name}")
    # 导入逻辑...

EOF
```

---

## ✅ 导入检查清单

- [ ] 文件格式正确（.docx）
- [ ] 文档包含标准的章节结构
- [ ] 标段编号格式正确（LW开头）
- [ ] 施工单位、监理单位信息完整
- [ ] 工点名称清晰
- [ ] 问题描述完整
- [ ] 导入后数据库中的数据正确
- [ ] 项目、标段、工点、问题的关系正确


