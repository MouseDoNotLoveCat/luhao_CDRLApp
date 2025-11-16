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

