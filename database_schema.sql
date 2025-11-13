-- ============================================================================
-- 工程隐患库管理应用 (CDRL) - 数据库初始化脚本
-- ============================================================================

-- 表 1: 监督通知书
CREATE TABLE IF NOT EXISTS supervision_notices (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  notice_number VARCHAR(100) UNIQUE NOT NULL,  -- 通知书编号（如：南宁站[2025]（通知）黄百11号）
  check_date DATE NOT NULL,  -- 检查日期
  check_unit VARCHAR(100) NOT NULL,  -- 检查单位（如：南宁监督站）
  check_personnel VARCHAR(500),  -- 检查人员（人名列表，用、分隔）
  inspection_basis TEXT,  -- 检查依据（文件名称和文号）

  -- 统计字段
  quality_issues_count INTEGER DEFAULT 0,  -- 质量问题数
  safety_issues_count INTEGER DEFAULT 0,  -- 安全问题数
  management_issues_count INTEGER DEFAULT 0,  -- 管理问题数
  total_issues_count INTEGER DEFAULT 0,  -- 问题总数

  -- 系统字段
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 更新时间
);

-- 表 2: 项目
CREATE TABLE IF NOT EXISTS projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_name VARCHAR(200) NOT NULL UNIQUE,  -- 项目名称（如：黄百铁路、柳梧铁路）
  builder_unit VARCHAR(100),  -- 建设单位（1个项目对应1个建设单位）

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 更新时间
);

-- 表 2.5: 标段（新增）
CREATE TABLE IF NOT EXISTS sections (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL,  -- 所属项目 ID
  section_name VARCHAR(200) NOT NULL,  -- 标段名称（如：太平隧道出口）
  contractor_unit VARCHAR(100),  -- 施工单位（1个标段对应1个施工单位）
  supervisor_unit VARCHAR(100),  -- 监理单位（1个标段对应1个监理单位）
  designer_unit VARCHAR(100),  -- 设计单位（1个标段对应1个设计单位）
  testing_unit VARCHAR(100),  -- 第三方检测单位（新增字段）

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 更新时间

  FOREIGN KEY (project_id) REFERENCES projects(id),
  UNIQUE(project_id, section_name)
);

-- 表 3: 隐患问题（直接关联到标段，包含工点名称）
CREATE TABLE IF NOT EXISTS issues (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  issue_number VARCHAR(100) UNIQUE NOT NULL,  -- 问题编号（如：(1)、(2)等）
  supervision_notice_id INTEGER NOT NULL,  -- 来自哪个监督通知书
  section_id INTEGER NOT NULL,  -- 属于哪个标段（直接关联）

  -- 工点信息
  site_name VARCHAR(200),  -- 工点名称（如"藤县北站"、"紫荆瑶山隧道出口"等）

  -- 问题分类（三层结构）
  issue_category VARCHAR(50),  -- 问题类别一级（工程质量/施工安全/管理行为/其它）
  issue_type_level1 VARCHAR(100),  -- 问题类别二级分类（混凝土工程、隧道施工等）
  issue_type_level2 VARCHAR(100),  -- 问题类别三级分类（原材料、洞口开挖等）

  -- 问题信息
  description TEXT NOT NULL,  -- 问题描述
  severity INTEGER DEFAULT 3,  -- 严重程度（1-6，1最严重）
  keywords VARCHAR(500),  -- 关键词（用于搜索和分类）

  -- 检查信息
  inspection_unit VARCHAR(100),  -- 检查单位（如：南宁监督站）
  inspection_date DATE,  -- 检查日期
  inspection_personnel VARCHAR(500),  -- 检查人员

  -- 整改信息
  rectification_requirements TEXT,  -- 整改要求（措施）
  rectification_deadline DATE,  -- 整改期限
  rectification_date DATE,  -- 整改完成日期
  rectification_status VARCHAR(50),  -- 整改状态（未整改/整改中/已整改/逾期）

  -- 销号信息
  closure_date DATE,  -- 销号日期
  closure_status VARCHAR(50),  -- 销号状态（未销号/已销号）
  closure_personnel VARCHAR(100),  -- 销号人员

  -- 问题类别（可多选）
  is_rectification_notice BOOLEAN DEFAULT FALSE,  -- 是否下发整改通知单
  is_bad_behavior_notice BOOLEAN DEFAULT FALSE,  -- 是否不良行为通知单

  -- 责任单位
  responsible_unit VARCHAR(100),  -- 责任单位（施工单位/监理单位等）
  responsible_person VARCHAR(100),  -- 整改责任人

  -- 文档识别字段
  document_section VARCHAR(50),  -- 文档章节（'rectification' 或 'other'）
  document_source VARCHAR(50),   -- 文档来源（'excel' 或 'word'）

  -- 系统字段
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 更新时间

  FOREIGN KEY (supervision_notice_id) REFERENCES supervision_notices(id),
  FOREIGN KEY (section_id) REFERENCES sections(id)
);

-- 表 5: 隐患处罚措施（支持多选）
CREATE TABLE IF NOT EXISTS issue_penalties (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  issue_id INTEGER NOT NULL,  -- 所属问题 ID
  penalty_type VARCHAR(50) NOT NULL,  -- 处罚类型（见下方可选值）

  -- penalty_type 可选值：
  -- rectification_order (责令改正)
  -- demolition_rework (拆除返工)
  -- temporary_suspension (临时停工)
  -- construction_general (施工一般)
  -- construction_major (施工较大)
  -- construction_severe (施工重大)
  -- supervision_general (监理一般)
  -- supervision_major (监理较大)
  -- supervision_severe (监理重大)

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间

  FOREIGN KEY (issue_id) REFERENCES issues(id) ON DELETE CASCADE
);

-- 表 6: 责任单位（可选，用于记录问题的具体责任人）
CREATE TABLE IF NOT EXISTS responsibility_units (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  issue_id INTEGER NOT NULL,  -- 所属问题 ID
  unit_type VARCHAR(50) NOT NULL,  -- 单位类型（建设/设计/施工/监理）
  unit_name VARCHAR(200),  -- 单位名称
  responsible_person VARCHAR(100),  -- 责任人姓名
  phone VARCHAR(20),  -- 联系电话

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 更新时间

  FOREIGN KEY (issue_id) REFERENCES issues(id) ON DELETE CASCADE
);

-- 注：单位信息主要存储在 projects 和 sections 表中
-- projects.builder_unit - 建设单位
-- sections.contractor_unit - 施工单位
-- sections.supervisor_unit - 监理单位
-- sections.designer_unit - 设计单位

-- 表 7: 问题图片
CREATE TABLE IF NOT EXISTS issue_images (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  issue_id INTEGER NOT NULL,  -- 所属问题 ID
  image_type VARCHAR(50),  -- 图片类型（问题/整改）
  image_path VARCHAR(500) NOT NULL,  -- 图片路径
  image_order INTEGER,  -- 图片顺序
  description VARCHAR(500),  -- 图片描述

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间

  FOREIGN KEY (issue_id) REFERENCES issues(id) ON DELETE CASCADE
);

-- ============================================================================
-- 索引
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_supervision_notices_check_date 
  ON supervision_notices(check_date);

CREATE INDEX IF NOT EXISTS idx_supervision_notices_check_unit 
  ON supervision_notices(check_unit);

CREATE INDEX IF NOT EXISTS idx_projects_project_name
  ON projects(project_name);

CREATE INDEX IF NOT EXISTS idx_sections_project_id
  ON sections(project_id);

CREATE INDEX IF NOT EXISTS idx_issues_issue_number
  ON issues(issue_number);

CREATE INDEX IF NOT EXISTS idx_issues_supervision_notice_id
  ON issues(supervision_notice_id);

CREATE INDEX IF NOT EXISTS idx_issues_section_id
  ON issues(section_id);

CREATE INDEX IF NOT EXISTS idx_issues_site_name
  ON issues(site_name);

CREATE INDEX IF NOT EXISTS idx_issues_issue_category 
  ON issues(issue_category);

CREATE INDEX IF NOT EXISTS idx_issues_severity 
  ON issues(severity);

CREATE INDEX IF NOT EXISTS idx_issues_inspection_date
  ON issues(inspection_date);

CREATE INDEX IF NOT EXISTS idx_issues_rectification_deadline
  ON issues(rectification_deadline);

CREATE INDEX IF NOT EXISTS idx_issues_rectification_date
  ON issues(rectification_date);

CREATE INDEX IF NOT EXISTS idx_issues_rectification_status
  ON issues(rectification_status);

CREATE INDEX IF NOT EXISTS idx_issues_closure_date
  ON issues(closure_date);

CREATE INDEX IF NOT EXISTS idx_issues_closure_status
  ON issues(closure_status);

CREATE INDEX IF NOT EXISTS idx_issues_is_rectification_notice
  ON issues(is_rectification_notice);

CREATE INDEX IF NOT EXISTS idx_issues_document_section
  ON issues(document_section);

CREATE INDEX IF NOT EXISTS idx_issues_document_source
  ON issues(document_source);

CREATE INDEX IF NOT EXISTS idx_issue_penalties_issue_id
  ON issue_penalties(issue_id);

CREATE INDEX IF NOT EXISTS idx_responsibility_units_issue_id 
  ON responsibility_units(issue_id);

CREATE INDEX IF NOT EXISTS idx_responsibility_units_unit_type 
  ON responsibility_units(unit_type);

CREATE INDEX IF NOT EXISTS idx_issue_images_issue_id 
  ON issue_images(issue_id);

-- ============================================================================
-- 初始化数据
-- ============================================================================

-- 问题类别初始化（可选）
-- INSERT INTO issue_categories (name, description) VALUES
--   ('质量', '工程质量相关问题'),
--   ('安全', '施工安全相关问题'),
--   ('管理', '管理行为相关问题');

-- 安全子类别初始化（可选）
-- INSERT INTO safety_subcategories (name, description) VALUES
--   ('防洪防汛', '防洪防汛相关隐患'),
--   ('消防安全', '消防防火相关隐患'),
--   ('隧道安全', '隧道施工安全隐患'),
--   ('桥梁安全', '桥梁施工安全隐患'),
--   ('劳动作业安全', '劳动作业安全隐患'),
--   ('交通安全', '交通安全隐患'),
--   ('营业线安全', '邻近既有线施工安全隐患');

-- ============================================================================
-- 视图（可选）
-- ============================================================================

-- 隐患统计视图
CREATE VIEW IF NOT EXISTS v_issues_summary AS
SELECT 
  s.notice_number,
  s.check_date,
  s.check_unit,
  COUNT(i.id) as total_issues,
  SUM(CASE WHEN i.issue_category = '质量' THEN 1 ELSE 0 END) as quality_count,
  SUM(CASE WHEN i.issue_category = '安全' THEN 1 ELSE 0 END) as safety_count,
  SUM(CASE WHEN i.issue_category = '管理' THEN 1 ELSE 0 END) as management_count
FROM supervision_notices s
LEFT JOIN issues i ON s.id = i.supervision_notice_id
GROUP BY s.id;

-- 整改进度视图
CREATE VIEW IF NOT EXISTS v_rectification_progress AS
SELECT
  i.issue_number,
  i.description,
  i.rectification_deadline,
  i.rectification_date,
  i.rectification_status,
  CASE
    WHEN i.rectification_date IS NULL THEN '未整改'
    WHEN i.rectification_date <= i.rectification_deadline THEN '按期完成'
    ELSE '逾期完成'
  END as status
FROM issues i
WHERE i.rectification_deadline IS NOT NULL;

-- 下发整改通知单统计视图 ⭐ 新增
CREATE VIEW IF NOT EXISTS v_rectification_notices_summary AS
SELECT
  s.notice_number,
  s.check_date,
  s.check_unit,
  COUNT(CASE WHEN i.is_rectification_notice = TRUE THEN 1 END) as rectification_notice_count,
  COUNT(CASE WHEN i.is_rectification_notice = FALSE THEN 1 END) as other_issues_count,
  COUNT(i.id) as total_issues
FROM supervision_notices s
LEFT JOIN issues i ON s.id = i.supervision_notice_id
GROUP BY s.id;

-- 问题分类视图 ⭐ 新增
CREATE VIEW IF NOT EXISTS v_issues_by_type AS
SELECT
  i.issue_number,
  i.description,
  i.site_name,
  i.issue_category,
  i.issue_type_level1,
  i.issue_type_level2,
  i.is_rectification_notice,
  i.is_bad_behavior_notice,
  i.document_section,
  i.document_source,
  i.severity,
  i.rectification_deadline,
  i.rectification_status
FROM issues i
ORDER BY i.is_rectification_notice DESC, i.severity DESC;

-- ============================================================================
-- 数据库初始化完成
-- ============================================================================

