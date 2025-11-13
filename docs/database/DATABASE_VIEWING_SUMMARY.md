# 📊 查看 cdrl.db 数据库 - 完整总结

**最后更新**：2025-10-24

---

## 🎯 3 种快速查看方法

### 方法 1️⃣：Python 脚本（最简单）⭐ 推荐

```bash
python3 view_db.py
```

**优点**：
- ✅ 一行命令
- ✅ 格式化输出
- ✅ 显示所有关键信息
- ✅ 无需安装额外工具

**输出内容**：
- 监督通知书列表
- 统计信息
- 按通知书统计
- 问题详情
- 下发整改通知单的问题
- 其它问题

### 方法 2️⃣：SQLite 命令行

```bash
sqlite3 backend/cdrl.db
```

**常用命令**：
```sql
-- 查看所有表
.tables

-- 查看监督通知书
SELECT * FROM supervision_notices;

-- 查看问题统计
SELECT COUNT(*) FROM issues;

-- 查看下发整改通知单的问题
SELECT * FROM issues WHERE is_rectification_notice = 1;

-- 退出
.quit
```

### 方法 3️⃣：API 接口

```bash
# 启动服务
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

# 在浏览器打开
http://localhost:8000/docs

# 或使用 curl
curl http://localhost:8000/api/statistics
curl http://localhost:8000/api/notices
curl http://localhost:8000/api/issues
```

---

## 📊 数据库内容概览

### 监督通知书（8 条）

```
1. 南宁站[2025]（通知）黄百10号 - 2025-08-20
2. 南宁站[2025]（通知）黄百08号 - 2025-07-15
3. 南宁站〔2025〕（通知）玉岑08号 - 2025-07-23
4. 南宁站〔2025〕（通知）柳梧11号 - 2025-10-13
5. 南宁站〔2025〕（通知）柳梧6号 - 2025-05-20
6. 编号：南宁站[2025]（通知）钦防二线 - 2025-08-07
7. 南宁站[2025]（通知）黄百11号 - 2025-09-09
8. 南宁站〔2025〕（通知）柳梧10号 - 2025-09-04
```

### 问题统计

| 指标 | 数值 |
|------|------|
| 总问题数 | 104 |
| 下发整改通知单 | 98 |
| 其它问题 | 6 |

### 按通知书统计

| 通知书编号 | 问题数 | 下发整改 | 其它问题 |
|-----------|--------|---------|---------|
| 南宁站〔2025〕（通知）柳梧6号 | 27 | 27 | 0 |
| 南宁站[2025]（通知）黄百10号 | 22 | 22 | 0 |
| 南宁站[2025]（通知）黄百11号 | 22 | 22 | 0 |
| 南宁站〔2025〕（通知）柳梧11号 | 14 | 14 | 0 |
| 南宁站[2025]（通知）黄百08号 | 13 | 13 | 0 |
| 编号：南宁站[2025]（通知）钦防二线 | 6 | 0 | 6 |

---

## 🛠️ 推荐工具

### 1. Python 脚本（已提供）

**文件**：`view_db.py`

**使用**：
```bash
python3 view_db.py
```

### 2. DB Browser for SQLite（推荐）

**下载**：https://sqlitebrowser.org/

**使用**：
1. 下载并安装
2. 打开应用
3. 点击"打开数据库"
4. 选择 `backend/cdrl.db`
5. 浏览数据

### 3. VS Code SQLite 扩展

**安装**：在 VS Code 中搜索 "SQLite" 扩展

**使用**：
1. 安装扩展
2. 右键点击 `backend/cdrl.db`
3. 选择"打开数据库"
4. 查看表和数据

### 4. Python pandas

```bash
pip install pandas
```

```python
import pandas as pd
import sqlite3

conn = sqlite3.connect('backend/cdrl.db')
df = pd.read_sql_query("SELECT * FROM supervision_notices", conn)
print(df)
conn.close()
```

---

## 📋 常用查询

### 查看所有通知书

```bash
sqlite3 backend/cdrl.db "SELECT id, notice_number, check_date FROM supervision_notices;"
```

### 查看问题统计

```bash
sqlite3 backend/cdrl.db "SELECT COUNT(*) as 总数, SUM(CASE WHEN is_rectification_notice = 1 THEN 1 ELSE 0 END) as 下发整改 FROM issues;"
```

### 查看下发整改通知单的问题

```bash
sqlite3 backend/cdrl.db "SELECT id, issue_number FROM issues WHERE is_rectification_notice = 1 LIMIT 10;"
```

### 查看其它问题

```bash
sqlite3 backend/cdrl.db "SELECT id, issue_number FROM issues WHERE is_rectification_notice = 0;"
```

### 按通知书统计

```bash
sqlite3 backend/cdrl.db << 'EOF'
SELECT 
  s.notice_number,
  COUNT(i.id) as 问题数,
  SUM(CASE WHEN i.is_rectification_notice = 1 THEN 1 ELSE 0 END) as 下发整改
FROM supervision_notices s
LEFT JOIN issues i ON s.id = i.supervision_notice_id
GROUP BY s.id
ORDER BY COUNT(i.id) DESC;
EOF
```

---

## 💾 导出数据

### 导出为 CSV

```bash
# 导出监督通知书
sqlite3 backend/cdrl.db << 'EOF'
.mode csv
.output supervision_notices.csv
SELECT * FROM supervision_notices;
.output stdout
EOF

# 导出问题
sqlite3 backend/cdrl.db << 'EOF'
.mode csv
.output issues.csv
SELECT * FROM issues;
.output stdout
EOF
```

### 导出为 Excel

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('backend/cdrl.db')

# 读取表
df_notices = pd.read_sql_query("SELECT * FROM supervision_notices", conn)
df_issues = pd.read_sql_query("SELECT * FROM issues", conn)

# 导出为 Excel
with pd.ExcelWriter('export.xlsx') as writer:
    df_notices.to_excel(writer, sheet_name='通知书', index=False)
    df_issues.to_excel(writer, sheet_name='问题', index=False)

conn.close()
print("✅ 导出成功: export.xlsx")
```

---

## 🔍 表结构

### supervision_notices（监督通知书）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| notice_number | VARCHAR | 通知书编号 |
| check_date | DATE | 检查日期 |
| check_unit | VARCHAR | 检查单位 |
| check_personnel | VARCHAR | 检查人员 |

### issues（隐患问题）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| issue_number | VARCHAR | 问题编号 |
| supervision_notice_id | INTEGER | 关联通知书 ID |
| description | TEXT | 问题描述 |
| is_rectification_notice | BOOLEAN | 是否下发整改通知单 |
| document_section | VARCHAR | 文档章节 |
| document_source | VARCHAR | 数据来源 |
| severity | INTEGER | 严重程度 |
| issue_category | VARCHAR | 问题分类 |

---

## 🎯 快速命令

```bash
# 查看数据库大小
ls -lh backend/cdrl.db

# 查看表数量
sqlite3 backend/cdrl.db ".tables"

# 查看表结构
sqlite3 backend/cdrl.db ".schema supervision_notices"

# 查看行数
sqlite3 backend/cdrl.db "SELECT COUNT(*) FROM supervision_notices;"

# 备份数据库
cp backend/cdrl.db backend/cdrl_backup.db

# 删除数据库（谨慎！）
rm backend/cdrl.db

# 重新初始化数据库
python backend/scripts/init_db.py
```

---

## 📚 相关文档

- **HOW_TO_VIEW_DATABASE.md** - 详细的查看指南
- **VIEW_DATABASE_GUIDE.md** - 完整的查看指南
- **QUICK_START_IMPORT.md** - 导入系统快速开始
- **IMPORT_EXECUTION_REPORT.md** - 导入执行报告

---

## 🚀 下一步

1. **查看数据**：运行 `python3 view_db.py` 查看数据
2. **分析数据**：使用 SQL 或 Python 进行数据分析
3. **导出数据**：导出为 CSV 或 Excel 格式
4. **开发前端**：基于数据库开发前端界面

---

**版本**：1.0

**最后更新**：2025-10-24


