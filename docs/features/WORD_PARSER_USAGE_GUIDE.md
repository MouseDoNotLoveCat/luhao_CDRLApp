# 📖 Word 解析器使用指南

**版本**: v3.0  
**最后更新**: 2025-10-24

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install python-docx
```

### 2. 基本使用

```python
from backend.app.parsers.word_parser import parse_word_document

# 解析 Word 文档
result = parse_word_document("path/to/document.docx")

# 获取识别结果
print(result['builder_unit'])           # 建设单位
print(result['inspection_unit'])        # 检查单位
print(result['inspection_personnel'])   # 检查人员
print(result['project_name'])           # 项目名称
print(result['notice_number'])          # 通知书编号
print(result['check_date'])             # 检查日期
```

### 3. 导入数据库

```bash
python backend/scripts/import_documents_v2.py
```

---

## 📋 识别字段说明

### 基本信息

| 字段 | 中文名 | 识别位置 | 示例 |
|------|--------|---------|------|
| `notice_number` | 通知书编号 | 文档开头 | 南宁站〔2025〕（通知）柳梧6号 |
| `check_date` | 检查日期 | 文档开头 | 2025-05-20 |
| `builder_unit` | 建设单位 | 编号下一行 | 柳州铁路工程建设指挥部 |

### 第一段话识别

| 字段 | 中文名 | 识别规则 | 示例 |
|------|--------|---------|------|
| `inspection_unit` | 检查单位 | 查找"监督站" | 南宁监督站 |
| `inspection_personnel` | 检查人员 | "监督站"和"对"之间 | 蒋德义、卢浩 |
| `project_name` | 项目名称 | "对"之后，包含"铁路" | 柳梧铁路 |

### 问题信息

| 字段 | 中文名 | 识别位置 | 示例 |
|------|--------|---------|------|
| `section_code` | 标段编号 | 工点信息 | LWZF-2 |
| `point_name` | 工点名称 | 工点信息 | LWZF-2标藤县北站 |
| `contractor` | 施工单位 | 工点信息 | 中铁上海局 |
| `supervisor` | 监理单位 | 工点信息 | 北京现代 |
| `inspection_date` | 检查日期 | 工点信息 | 2025-05-21 |

---

## 🔧 API 参考

### parse_word_document(file_path: str) -> Dict

**功能**：解析 Word 文档

**参数**：
- `file_path` (str): Word 文件路径

**返回值**：
```python
{
    'file_name': str,                    # 文件名
    'status': str,                       # 'success' 或 'error'
    'notice_number': str,                # 通知书编号
    'check_date': str,                   # 检查日期
    'builder_unit': str,                 # 建设单位
    'inspection_unit': str,              # 检查单位
    'inspection_personnel': str,         # 检查人员
    'project_name': str,                 # 项目名称
    'rectification_notices': List[Dict], # 下发整改通知单
    'other_issues': List[Dict],          # 其它问题
    'total_issues': int,                 # 总问题数
    'error': str                         # 错误信息（如果有）
}
```

### WordDocumentParser 类

**初始化**：
```python
from backend.app.parsers.word_parser import WordDocumentParser

parser = WordDocumentParser("path/to/document.docx")
result = parser.parse()
```

**主要方法**：
- `parse()` - 解析文档
- `_extract_builder_unit()` - 提取建设单位
- `_extract_inspection_unit_from_first_para()` - 提取检查单位
- `_extract_inspection_personnel_from_first_para()` - 提取检查人员
- `_extract_project_name_from_first_para()` - 提取项目名称
- `_extract_check_date_from_para()` - 提取检查日期

---

## 📝 使用示例

### 示例 1：解析单个文件

```python
from backend.app.parsers.word_parser import parse_word_document

file_path = "Samples/柳梧铁路内部监督通知书（编号：南宁站[2025]（通知）柳梧6号）-1.docx"
result = parse_word_document(file_path)

if result['status'] == 'success':
    print(f"项目: {result['project_name']}")
    print(f"建设单位: {result['builder_unit']}")
    print(f"检查单位: {result['inspection_unit']}")
    print(f"检查人员: {result['inspection_personnel']}")
    print(f"问题数: {result['total_issues']}")
else:
    print(f"错误: {result['error']}")
```

### 示例 2：批量导入

```bash
# 导入单个文件
python backend/scripts/import_documents_v2.py

# 或修改脚本支持批量导入
```

### 示例 3：访问问题详情

```python
result = parse_word_document(file_path)

# 访问下发整改通知单
for issue in result['rectification_notices']:
    print(f"标段: {issue['section_code']}")
    print(f"工点: {issue['point_name']}")
    print(f"施工单位: {issue['contractor']}")
    print(f"监理单位: {issue['supervisor']}")
    print(f"检查单位: {issue['inspection_unit']}")
    print(f"检查人员: {issue['inspection_personnel']}")
    print(f"检查日期: {issue['inspection_date']}")
```

---

## ⚠️ 注意事项

### 文档格式要求

1. **通知书编号**：必须在文档开头
2. **建设单位**：必须在编号下一行，包含"指挥部"或"公司"
3. **第一段话**：必须包含"监督站"、"对"和"铁路"
4. **工点信息**：必须包含标段编号（如 LWZF-2）和检查日期

### 常见问题

**Q: 识别失败怎么办？**
A: 检查文档格式是否符合要求，查看错误信息

**Q: 如何处理格式变化？**
A: 修改正则表达式规则，或提交 Issue

**Q: 如何添加新的识别字段？**
A: 在 WordDocumentParser 类中添加新方法

---

## 🔍 调试技巧

### 1. 查看文档结构

```python
from docx import Document

doc = Document("path/to/document.docx")
for i, para in enumerate(doc.paragraphs[:20]):
    print(f"{i}: {para.text}")
```

### 2. 测试单个识别方法

```python
from backend.app.parsers.word_parser import WordDocumentParser

parser = WordDocumentParser("path/to/document.docx")
parser.doc = Document("path/to/document.docx")
parser._extract_paragraphs()

# 测试各个方法
print(parser._extract_builder_unit())
print(parser._extract_inspection_unit_from_first_para())
print(parser._extract_inspection_personnel_from_first_para())
print(parser._extract_project_name_from_first_para())
```

### 3. 查看解析结果

```python
import json

result = parse_word_document(file_path)
print(json.dumps(result, indent=2, ensure_ascii=False))
```

---

## 📚 相关文档

- `WORD_PARSER_IMPROVEMENT_SUMMARY.md` - 改进总结
- `IMPLEMENTATION_COMPLETE_SUMMARY.md` - 实现完成总结
- `DATABASE_STRUCTURE_DETAILED.md` - 数据库详细设计


