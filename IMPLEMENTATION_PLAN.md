# 导入功能架构调整实施方案

## 📋 概述

通过移除 `issues` 表的 `section_id` 外键约束，改为直接存储 `section_name` 文本字段，解决标段识别失败导致导入失败的问题。

---

## 1️⃣ 数据库迁移方案

### 1.1 迁移策略

**采用 SQLite 的 ALTER TABLE 限制处理方案**：
- SQLite 不支持直接删除列，需要通过重建表的方式
- 创建新表 → 复制数据 → 删除旧表 → 重命名新表

### 1.2 具体迁移步骤

#### 步骤 1：创建迁移脚本 `backend/scripts/migrate_issues_table.sql`

```sql
-- 步骤 1: 创建新表（不含 section_id 外键，新增 section_name）
CREATE TABLE issues_new (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  issue_number VARCHAR(100) UNIQUE NOT NULL,
  supervision_notice_id INTEGER NOT NULL,
  
  -- 新增：直接存储标段名称
  section_name VARCHAR(200),
  
  -- 工点信息
  site_name VARCHAR(200),
  
  -- 问题分类（三层结构）
  issue_category VARCHAR(50),
  issue_type_level1 VARCHAR(100),
  issue_type_level2 VARCHAR(100),
  
  -- 问题信息
  description TEXT NOT NULL,
  severity INTEGER DEFAULT 3,
  keywords VARCHAR(500),
  
  -- 检查信息
  inspection_unit VARCHAR(100),
  inspection_date DATE,
  inspection_personnel VARCHAR(500),
  
  -- 整改信息
  rectification_requirements TEXT,
  rectification_deadline DATE,
  rectification_date DATE,
  rectification_status VARCHAR(50),
  
  -- 销号信息
  closure_date DATE,
  closure_status VARCHAR(50),
  closure_personnel VARCHAR(100),
  
  -- 问题类别
  is_rectification_notice BOOLEAN DEFAULT FALSE,
  is_bad_behavior_notice BOOLEAN DEFAULT FALSE,
  
  -- 责任单位
  responsible_unit VARCHAR(100),
  responsible_person VARCHAR(100),
  
  -- 文档识别字段
  document_section VARCHAR(50),
  document_source VARCHAR(50),
  
  -- 系统字段
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (supervision_notice_id) REFERENCES supervision_notices(id)
);

-- 步骤 2: 从旧表复制数据（section_id 转换为 section_name）
INSERT INTO issues_new (
  id, issue_number, supervision_notice_id, section_name, site_name,
  issue_category, issue_type_level1, issue_type_level2, description,
  severity, keywords, inspection_unit, inspection_date, inspection_personnel,
  rectification_requirements, rectification_deadline, rectification_date,
  rectification_status, closure_date, closure_status, closure_personnel,
  is_rectification_notice, is_bad_behavior_notice, responsible_unit,
  responsible_person, document_section, document_source, created_at, updated_at
)
SELECT
  i.id, i.issue_number, i.supervision_notice_id,
  COALESCE(s.section_name, '未知标段') as section_name,
  i.site_name, i.issue_category, i.issue_type_level1, i.issue_type_level2,
  i.description, i.severity, i.keywords, i.inspection_unit, i.inspection_date,
  i.inspection_personnel, i.rectification_requirements, i.rectification_deadline,
  i.rectification_date, i.rectification_status, i.closure_date, i.closure_status,
  i.closure_personnel, i.is_rectification_notice, i.is_bad_behavior_notice,
  i.responsible_unit, i.responsible_person, i.document_section, i.document_source,
  i.created_at, i.updated_at
FROM issues i
LEFT JOIN sections s ON i.section_id = s.id;

-- 步骤 3: 删除旧表
DROP TABLE issues;

-- 步骤 4: 重命名新表
ALTER TABLE issues_new RENAME TO issues;

-- 步骤 5: 重建索引
CREATE INDEX idx_issues_issue_number ON issues(issue_number);
CREATE INDEX idx_issues_supervision_notice_id ON issues(supervision_notice_id);
CREATE INDEX idx_issues_site_name ON issues(site_name);
CREATE INDEX idx_issues_issue_category ON issues(issue_category);
CREATE INDEX idx_issues_severity ON issues(severity);
CREATE INDEX idx_issues_inspection_date ON issues(inspection_date);
CREATE INDEX idx_issues_rectification_deadline ON issues(rectification_deadline);
CREATE INDEX idx_issues_rectification_date ON issues(rectification_date);
CREATE INDEX idx_issues_rectification_status ON issues(rectification_status);
CREATE INDEX idx_issues_closure_date ON issues(closure_date);
CREATE INDEX idx_issues_closure_status ON issues(closure_status);
CREATE INDEX idx_issues_is_rectification_notice ON issues(is_rectification_notice);
CREATE INDEX idx_issues_document_section ON issues(document_section);
CREATE INDEX idx_issues_document_source ON issues(document_source);
```

### 1.3 数据迁移影响分析

| 项目 | 说明 |
|------|------|
| **现有数据** | 所有现有问题的 `section_id` 将转换为对应的 `section_name` |
| **数据丢失** | 无。如果 `section_id` 无效，使用 '未知标段' 作为默认值 |
| **外键约束** | 移除 `section_id` 外键，保留 `supervision_notice_id` 外键 |
| **索引** | 移除 `idx_issues_section_id`，保留其他所有索引 |

---

## 2️⃣ 后端代码修改方案

### 2.1 修改文件：`backend/app/services/import_service.py`

#### 修改 1：`_insert_issue` 方法（第 244-385 行）

**当前问题**：
- 复杂的标段匹配逻辑（ProjectSectionMatcher）
- 标段插入失败导致 `section_id` 为 None
- 问题插入失败

**修改方案**：
- 移除所有标段匹配和插入逻辑
- 直接使用 `issue.get('section_name')` 作为标段名称
- 简化为直接插入问题

**修改代码**（约 50 行）：
```python
def _insert_issue(self, cursor, notice_id: int, issue: Dict, project_id: int) -> Optional[int]:
    """插入隐患问题"""
    try:
        # 直接获取标段名称（不再进行匹配和插入）
        section_name = issue.get('section_name', '未知标段')
        
        logger.info(f"\n[DEBUG] 准备插入问题记录:")
        logger.info(f"   section_name: {section_name}")
        logger.info(f"   description: {issue['description'][:100]}...")
        
        # 生成问题编号
        issue_number = f"ISSUE_{notice_id}_{datetime.now().timestamp()}"
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 自动分类
        issue_category = IssueCategoryClassifier.classify(
            description=issue['description'],
            site_name=issue.get('site_name'),
            section_name=section_name
        )
        if not issue_category or issue_category == '其它':
            issue_category = '施工安全'
        
        # 直接插入问题（不再需要 section_id）
        cursor.execute("""
            INSERT INTO issues
            (issue_number, supervision_notice_id, section_name, site_name, description,
             is_rectification_notice, is_bad_behavior_notice, document_section, document_source,
             severity, issue_category, inspection_unit, inspection_date, inspection_personnel,
             rectification_requirements, rectification_deadline, responsible_unit,
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            issue_number, notice_id, section_name, issue.get('site_name'),
            issue['description'], issue['is_rectification_notice'],
            issue.get('is_bad_behavior_notice', False), issue['document_section'],
            'word', 3, issue_category, issue.get('inspection_unit'),
            issue.get('inspection_date'), issue.get('inspection_personnel'),
            issue.get('rectification_requirements'), issue.get('rectification_deadline'),
            issue.get('responsible_unit'), now, now
        ))
        
        issue_id = cursor.lastrowid
        logger.info(f"[DEBUG] ✅ 问题插入成功: issue_id={issue_id}")
        return issue_id
        
    except Exception as e:
        logger.error(f"[ERROR] ❌ 问题插入失败: {e}")
        logger.error(traceback.format_exc())
        return None
```

#### 修改 2：移除不再需要的导入

- 移除 `from .project_section_matcher import ProjectSectionMatcher`
- 保留 `from .issue_category_classifier import IssueCategoryClassifier`

### 2.2 修改文件：`database_schema.sql`

更新 `issues` 表的创建语句，移除 `section_id` 外键，添加 `section_name` 字段。

---

## 3️⃣ 前端代码修改方案

### 3.1 修改文件：`frontend/src/components/ImportConfirm.vue`

**当前状态**：已显示 `section_name` 字段

**需要的改进**：
- 添加行内编辑功能
- 添加标段下拉选择
- 显示更多字段

### 3.2 修改文件：`frontend/src/stores/importStore.js`

**需要的改进**：
- 添加标段列表获取方法
- 添加字段编辑状态管理
- 添加验证逻辑

---

## 4️⃣ 潜在风险和注意事项

| 风险 | 影响 | 缓解方案 |
|------|------|---------|
| **数据迁移失败** | 现有问题数据丢失 | 迁移前备份数据库 |
| **外键约束冲突** | 迁移过程中出错 | 先禁用外键检查 |
| **应用兼容性** | 其他代码引用 `section_id` | 全局搜索并更新所有引用 |
| **查询性能** | 失去 `section_id` 索引 | 添加 `section_name` 索引 |

---

## 5️⃣ 实施顺序

1. ✅ 备份数据库
2. ⏳ 执行数据库迁移脚本
3. ⏳ 修改后端代码
4. ⏳ 修改前端代码
5. ⏳ 测试导入功能
6. ⏳ 验证现有问题查询功能

---

## 6️⃣ 替代方案对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| **当前方案**（移除外键） | 简单、快速、解决根本问题 | 失去数据库级别的标段关联 |
| **改进标段匹配** | 保留外键、数据完整性好 | 复杂、容易出错、时间长 |
| **添加标段管理界面** | 用户友好 | 需要额外开发、时间长 |

**推荐**：当前方案最优，因为：
- 导入时用户可以手动修正标段名称
- 标段管理通过 `sections` 表独立进行
- 问题和标段的关系通过文本匹配而非外键


