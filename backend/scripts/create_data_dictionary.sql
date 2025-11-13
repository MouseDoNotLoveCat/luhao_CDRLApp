-- ============================================================================
-- 数据字典表（可选）
-- 用于在数据库中存储表和字段的元数据信息
-- ============================================================================

-- 表 1: 表元数据
CREATE TABLE IF NOT EXISTS table_schema (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  table_name VARCHAR(100) NOT NULL UNIQUE,  -- 表名
  table_name_cn VARCHAR(100) NOT NULL,  -- 表中文名称
  description TEXT,  -- 表描述
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 表 2: 字段元数据
CREATE TABLE IF NOT EXISTS column_schema (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  table_name VARCHAR(100) NOT NULL,  -- 表名
  column_name VARCHAR(100) NOT NULL,  -- 字段名
  column_name_cn VARCHAR(100) NOT NULL,  -- 字段中文名称
  data_type VARCHAR(50),  -- 数据类型
  is_nullable BOOLEAN DEFAULT TRUE,  -- 是否可为空
  is_primary_key BOOLEAN DEFAULT FALSE,  -- 是否主键
  is_foreign_key BOOLEAN DEFAULT FALSE,  -- 是否外键
  default_value VARCHAR(100),  -- 默认值
  description TEXT,  -- 字段描述
  example VARCHAR(200),  -- 示例值
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  UNIQUE(table_name, column_name)
);

-- ============================================================================
-- 初始化表元数据
-- ============================================================================

INSERT INTO table_schema (table_name, table_name_cn, description) VALUES
  ('supervision_notices', '监督通知书', '存储监督通知书的基本信息'),
  ('projects', '项目', '存储铁路项目的基本信息'),
  ('sections', '标段', '存储项目下的标段信息'),
  ('issues', '隐患问题', '存储检查发现的隐患问题'),
  ('issue_penalties', '隐患处罚措施', '存储问题的处罚措施（支持多选）'),
  ('responsibility_units', '责任单位', '存储问题的具体责任单位和责任人'),
  ('issue_images', '问题图片', '存储问题相关的图片信息');

-- ============================================================================
-- 初始化字段元数据 - supervision_notices 表
-- ============================================================================

INSERT INTO column_schema (table_name, column_name, column_name_cn, data_type, is_nullable, is_primary_key, default_value, description, example) VALUES
  ('supervision_notices', 'id', 'ID', 'INTEGER', FALSE, TRUE, NULL, '主键', '1'),
  ('supervision_notices', 'notice_number', '通知书编号', 'VARCHAR(100)', FALSE, FALSE, NULL, '通知书编号', '南宁站[2025]（通知）黄百11号'),
  ('supervision_notices', 'check_date', '检查日期', 'DATE', FALSE, FALSE, NULL, '检查日期', '2025-09-09'),
  ('supervision_notices', 'check_unit', '检查单位', 'VARCHAR(100)', FALSE, FALSE, NULL, '检查单位（如：南宁监督站）', '南宁监督站'),
  ('supervision_notices', 'check_personnel', '检查人员', 'VARCHAR(500)', TRUE, FALSE, NULL, '检查人员（人名列表，用、分隔）', '卢浩、陈胜及建设部第四检查组胡云龙'),
  ('supervision_notices', 'inspection_basis', '检查依据', 'TEXT', TRUE, FALSE, NULL, '检查依据（文件名称和文号）', '根据《国铁集团关于...》等文件'),
  ('supervision_notices', 'quality_issues_count', '质量问题数', 'INTEGER', FALSE, FALSE, '0', '质量问题数', '27'),
  ('supervision_notices', 'safety_issues_count', '安全问题数', 'INTEGER', FALSE, FALSE, '0', '安全问题数', '29'),
  ('supervision_notices', 'management_issues_count', '管理问题数', 'INTEGER', FALSE, FALSE, '0', '管理问题数', '23'),
  ('supervision_notices', 'total_issues_count', '问题总数', 'INTEGER', FALSE, FALSE, '0', '问题总数', '79'),
  ('supervision_notices', 'created_at', '创建时间', 'TIMESTAMP', FALSE, FALSE, 'CURRENT_TIMESTAMP', '创建时间', '2025-11-05 10:00:00'),
  ('supervision_notices', 'updated_at', '更新时间', 'TIMESTAMP', FALSE, FALSE, 'CURRENT_TIMESTAMP', '更新时间', '2025-11-05 10:00:00');

-- ============================================================================
-- 初始化字段元数据 - projects 表
-- ============================================================================

INSERT INTO column_schema (table_name, column_name, column_name_cn, data_type, is_nullable, is_primary_key, default_value, description, example) VALUES
  ('projects', 'id', 'ID', 'INTEGER', FALSE, TRUE, NULL, '主键', '1'),
  ('projects', 'project_name', '项目名称', 'VARCHAR(200)', FALSE, FALSE, NULL, '项目名称', '黄百铁路'),
  ('projects', 'builder_unit', '建设单位', 'VARCHAR(100)', TRUE, FALSE, NULL, '建设单位（1个项目对应1个建设单位）', '云桂铁路广西有限责任公司'),
  ('projects', 'created_at', '创建时间', 'TIMESTAMP', FALSE, FALSE, 'CURRENT_TIMESTAMP', '创建时间', '2025-11-05 10:00:00'),
  ('projects', 'updated_at', '更新时间', 'TIMESTAMP', FALSE, FALSE, 'CURRENT_TIMESTAMP', '更新时间', '2025-11-05 10:00:00');

-- ============================================================================
-- 初始化字段元数据 - sections 表
-- ============================================================================

INSERT INTO column_schema (table_name, column_name, column_name_cn, data_type, is_nullable, is_primary_key, is_foreign_key, default_value, description, example) VALUES
  ('sections', 'id', 'ID', 'INTEGER', FALSE, TRUE, FALSE, NULL, '主键', '1'),
  ('sections', 'project_id', '项目ID', 'INTEGER', FALSE, FALSE, TRUE, NULL, '所属项目 ID', '1'),
  ('sections', 'section_code', '标段编号', 'VARCHAR(100)', FALSE, FALSE, FALSE, NULL, '标段编号', 'LWZQ-8'),
  ('sections', 'section_name', '标段名称', 'VARCHAR(200)', TRUE, FALSE, FALSE, NULL, '标段名称', '太平隧道出口'),
  ('sections', 'contractor_unit', '施工单位', 'VARCHAR(100)', TRUE, FALSE, FALSE, NULL, '施工单位（1个标段对应1个施工单位）', '中建八局'),
  ('sections', 'supervisor_unit', '监理单位', 'VARCHAR(100)', TRUE, FALSE, FALSE, NULL, '监理单位（1个标段对应1个监理单位）', '甘肃铁科'),
  ('sections', 'designer_unit', '设计单位', 'VARCHAR(100)', TRUE, FALSE, FALSE, NULL, '设计单位（1个标段对应1个设计单位）', '中铁设计'),
  ('sections', 'created_at', '创建时间', 'TIMESTAMP', FALSE, FALSE, FALSE, 'CURRENT_TIMESTAMP', '创建时间', '2025-11-05 10:00:00'),
  ('sections', 'updated_at', '更新时间', 'TIMESTAMP', FALSE, FALSE, FALSE, 'CURRENT_TIMESTAMP', '更新时间', '2025-11-05 10:00:00');

-- ============================================================================
-- 创建查询视图 - 查看表的字段信息
-- ============================================================================

CREATE VIEW IF NOT EXISTS v_table_columns AS
SELECT 
  ts.table_name_cn as '表名',
  cs.column_name as '字段名',
  cs.column_name_cn as '字段中文名',
  cs.data_type as '数据类型',
  CASE WHEN cs.is_nullable = 1 THEN '是' ELSE '否' END as '可为空',
  CASE WHEN cs.is_primary_key = 1 THEN '是' ELSE '否' END as '主键',
  CASE WHEN cs.is_foreign_key = 1 THEN '是' ELSE '否' END as '外键',
  cs.default_value as '默认值',
  cs.description as '描述',
  cs.example as '示例'
FROM table_schema ts
LEFT JOIN column_schema cs ON ts.table_name = cs.table_name
ORDER BY ts.id, cs.id;

-- ============================================================================
-- 使用示例
-- ============================================================================

-- 查看所有表的字段信息
-- SELECT * FROM v_table_columns;

-- 查看特定表的字段信息
-- SELECT * FROM v_table_columns WHERE 表名 = '监督通知书';

-- 查看所有表的描述
-- SELECT table_name, table_name_cn, description FROM table_schema;

-- 查看特定字段的详细信息
-- SELECT * FROM column_schema WHERE table_name = 'supervision_notices' AND column_name = 'notice_number';

