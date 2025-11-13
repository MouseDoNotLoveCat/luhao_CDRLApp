# 📊 查看 cdrl.db 数据库 - 完整指南

**最后更新**：2025-10-24

---

## 🎯 快速查看

### 方法 1：命令行查看（最简单）

```bash
# 进入数据库
sqlite3 backend/cdrl.db

# 查看所有表
.tables

# 查看监督通知书
SELECT * FROM supervision_notices;

# 查看问题
SELECT * FROM issues LIMIT 5;

# 退出
.quit
```

### 方法 2：Python 脚本查看（推荐）

```bash
python3 << 'EOF'
import sqlite3

# 连接数据库
conn = sqlite3.connect('backend/cdrl.db')
cursor = conn.cursor()

# 查看监督通知书
cursor.execute("SELECT * FROM supervision_notices")
for row in cursor.fetchall():
    print(row)

conn.close()
EOF
```

### 方法 3：API 接口查看（最方便）

```bash
# 启动服务
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

# 在浏览器打开
http://localhost:8000/docs
```

---

## 📋 详细查看方法

### 1️⃣ 查看监督通知书

#### 命令行方式

```bash
sqlite3 backend/cdrl.db
```

```sql
-- 查看所有通知书
SELECT id, notice_number, check_date, check_unit FROM supervision_notices;

-- 查看通知书详情
SELECT * FROM supervision_notices;

-- 按日期排序
SELECT id, notice_number, check_date FROM supervision_notices ORDER BY check_date DESC;

-- 统计通知书数量
SELECT COUNT(*) as 总数 FROM supervision_notices;
```

#### Python 脚本方式

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('backend/cdrl.db')

# 方式 1：使用 pandas（推荐）
df = pd.read_sql_query("SELECT * FROM supervision_notices", conn)
print(df)

# 方式 2：使用 cursor
cursor = conn.cursor()
cursor.execute("SELECT * FROM supervision_notices")
for row in cursor.fetchall():
    print(row)

conn.close()
```

#### API 方式

```bash
# 获取通知书列表
curl http://localhost:8000/api/notices?limit=10

# 获取统计信息
curl http://localhost:8000/api/statistics
```

---

### 2️⃣ 查看隐患问题

#### 命令行方式

```bash
sqlite3 backend/cdrl.db
```

```sql
-- 查看所有问题
SELECT id, issue_number, description, is_rectification_notice FROM issues;

-- 查看下发整改通知单的问题
SELECT id, issue_number, description FROM issues WHERE is_rectification_notice = 1;

-- 查看其它问题
SELECT id, issue_number, description FROM issues WHERE is_rectification_notice = 0;

-- 统计问题数量
SELECT 
  COUNT(*) as 总数,
  SUM(CASE WHEN is_rectification_notice = 1 THEN 1 ELSE 0 END) as 下发整改,
  SUM(CASE WHEN is_rectification_notice = 0 THEN 1 ELSE 0 END) as 其它问题
FROM issues;

-- 查看问题详情（包括描述）
SELECT id, issue_number, description, is_rectification_notice, document_section 
FROM issues 
LIMIT 5;
```

#### Python 脚本方式

```python
import sqlite3

conn = sqlite3.connect('backend/cdrl.db')
cursor = conn.cursor()

# 查看所有问题
cursor.execute("SELECT id, issue_number, description, is_rectification_notice FROM issues")
for row in cursor.fetchall():
    print(f"ID: {row[0]}")
    print(f"编号: {row[1]}")
    print(f"描述: {row[2][:100]}...")
    print(f"下发整改: {row[3]}")
    print("-" * 80)

conn.close()
```

#### API 方式

```bash
# 获取所有问题
curl http://localhost:8000/api/issues?limit=10

# 获取下发整改通知单的问题
curl "http://localhost:8000/api/issues?limit=10&is_rectification=true"

# 获取其它问题
curl "http://localhost:8000/api/issues?limit=10&is_rectification=false"
```

---

### 3️⃣ 查看统计信息

#### 命令行方式

```bash
sqlite3 backend/cdrl.db
```

```sql
-- 问题统计
SELECT 
  COUNT(*) as 总问题数,
  SUM(CASE WHEN is_rectification_notice = 1 THEN 1 ELSE 0 END) as 下发整改通知单,
  SUM(CASE WHEN is_rectification_notice = 0 THEN 1 ELSE 0 END) as 其它问题
FROM issues;

-- 按严重程度统计
SELECT severity, COUNT(*) as 数量 FROM issues GROUP BY severity;

-- 按分类统计
SELECT issue_category, COUNT(*) as 数量 FROM issues GROUP BY issue_category;

-- 按通知书统计
SELECT 
  s.notice_number,
  COUNT(i.id) as 问题数,
  SUM(CASE WHEN i.is_rectification_notice = 1 THEN 1 ELSE 0 END) as 下发整改,
  SUM(CASE WHEN i.is_rectification_notice = 0 THEN 1 ELSE 0 END) as 其它问题
FROM supervision_notices s
LEFT JOIN issues i ON s.id = i.supervision_notice_id
GROUP BY s.id;
```

#### Python 脚本方式

```python
import sqlite3

conn = sqlite3.connect('backend/cdrl.db')
cursor = conn.cursor()

# 统计问题
cursor.execute("""
  SELECT 
    COUNT(*) as 总数,
    SUM(CASE WHEN is_rectification_notice = 1 THEN 1 ELSE 0 END) as 下发整改,
    SUM(CASE WHEN is_rectification_notice = 0 THEN 1 ELSE 0 END) as 其它问题
  FROM issues
""")
row = cursor.fetchone()
print(f"总问题数: {row[0]}")
print(f"下发整改通知单: {row[1]}")
print(f"其它问题: {row[2]}")

conn.close()
```

#### API 方式

```bash
curl http://localhost:8000/api/statistics
```

**响应**：
```json
{
  "supervision_notices": 8,
  "total_issues": 104,
  "rectification_notices": 98,
  "other_issues": 6
}
```

---

## 🛠️ 推荐工具

### 1. SQLite 命令行（免费）

```bash
# Mac/Linux
sqlite3 backend/cdrl.db

# Windows
sqlite3.exe backend/cdrl.db
```

**优点**：
- 免费
- 无需安装
- 功能完整

**缺点**：
- 界面不友好
- 需要学习 SQL

### 2. DB Browser for SQLite（推荐）

**下载**：https://sqlitebrowser.org/

**优点**：
- 图形界面
- 易于使用
- 支持导出

**缺点**：
- 需要安装

### 3. Python pandas（推荐用于分析）

```bash
pip install pandas
```

```python
import pandas as pd
import sqlite3

conn = sqlite3.connect('backend/cdrl.db')

# 读取表
df = pd.read_sql_query("SELECT * FROM supervision_notices", conn)
print(df)

# 导出为 CSV
df.to_csv('supervision_notices.csv', index=False)

conn.close()
```

### 4. VS Code SQLite 扩展

**安装**：在 VS Code 中搜索 "SQLite" 扩展

**优点**：
- 集成在编辑器中
- 易于使用
- 支持查询

---

## 📊 常用查询示例

### 查询 1：查看所有通知书及其问题数

```sql
SELECT 
  s.id,
  s.notice_number,
  s.check_date,
  COUNT(i.id) as 问题数
FROM supervision_notices s
LEFT JOIN issues i ON s.id = i.supervision_notice_id
GROUP BY s.id
ORDER BY s.check_date DESC;
```

### 查询 2：查看下发整改通知单的问题详情

```sql
SELECT 
  i.id,
  i.issue_number,
  i.description,
  s.notice_number,
  s.check_date
FROM issues i
LEFT JOIN supervision_notices s ON i.supervision_notice_id = s.id
WHERE i.is_rectification_notice = 1
LIMIT 10;
```

### 查询 3：查看问题分布

```sql
SELECT 
  issue_category,
  COUNT(*) as 数量,
  ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM issues), 2) as 百分比
FROM issues
GROUP BY issue_category;
```

### 查询 4：查看严重程度分布

```sql
SELECT 
  severity,
  COUNT(*) as 数量
FROM issues
GROUP BY severity
ORDER BY severity;
```

---

## 💾 导出数据

### 导出为 CSV

```bash
sqlite3 backend/cdrl.db
```

```sql
.mode csv
.output supervision_notices.csv
SELECT * FROM supervision_notices;
.output stdout
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

## 🔍 表结构说明

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
```

---

**版本**：1.0

**最后更新**：2025-10-24


