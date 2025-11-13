# 📄 Word 文档解析指南

## 🎯 监督通知书结构识别

### 文档结构概览

监督通知书（.docx）通常包含以下主要章节：

```
1. 文档头部
   ├─ 签发
   ├─ 标题：内部监督通知书
   ├─ 编号：南宁站[2025]（通知）钦防二线 08号
   └─ 收文单位

2. 总体情况
   ├─ 检查时间
   ├─ 检查单位
   ├─ 检查范围
   ├─ 问题统计
   └─ 检查方法

3. 二、下发整改通知单的工点及问题 ⭐ 关键章节
   ├─ 工点 1
   │  ├─ 工点名称
   │  ├─ 检查时间
   │  ├─ 检查情况
   │  └─ 处理措施
   ├─ 工点 2
   └─ ...

4. 三、存在的其它主要安全质量等问题
   ├─ 工点 1
   │  ├─ 问题 1
   │  ├─ 问题 2
   │  └─ ...
   ├─ 工点 2
   └─ ...

5. 四、监督意见及整改要求
   └─ 整改要求

6. 附件
   ├─ 图片
   └─ 其他附件
```

---

## 🔍 章节识别规则

### 关键章节标识

| 章节 | 标识符 | 说明 | 问题类型 |
|------|--------|------|--------|
| **下发整改通知单** | "二、下发整改通知单" | 已下发整改通知单的问题 | ✅ is_rectification_notice = true |
| **其它问题** | "三、存在的其它" | 未下发整改通知单的问题 | ❌ is_rectification_notice = false |
| **监督意见** | "四、监督意见" | 整体监督意见 | 不作为单独问题 |

### 识别算法

```python
def identify_section(paragraph_text):
    """识别段落所属的章节"""
    
    if "二、下发整改通知单" in paragraph_text:
        return "RECTIFICATION_NOTICE_SECTION"
    
    elif "三、存在的其它" in paragraph_text:
        return "OTHER_ISSUES_SECTION"
    
    elif "四、监督意见" in paragraph_text:
        return "SUPERVISION_OPINION_SECTION"
    
    else:
        return "OTHER_SECTION"
```

---

## 📋 问题提取规则

### 下发整改通知单的问题

**位置**：第二章节

**结构**：
```
1. 工点名称（检查时间）
   检查情况：问题描述
   处理措施：处理方式、整改期限、处罚措施
```

**示例**：
```
1．中铁三局施工，广西宁铁监理的QFSG1标皇马隧道出口（检查时间2025年8月7日）
检查情况：用于隧道纵向施工缝的水泥基渗透结晶型防水涂料经查无进场验收记录，原材料未检先用。
处理措施：向施工单位下发《整改通知单》（南宁站钦防二线〔2025〕（改字）06号）责令改正，2025年8月20日前完成整改，当期信用评价中扣1分。
```

**提取字段**：
- issue_number: 从"整改通知单"编号提取
- description: 从"检查情况"提取
- rectification_measures: 从"处理措施"提取
- deadline: 从"处理措施"中的日期提取
- penalty_type: 从"处理措施"中的处罚措施提取（如"责令改正"）
- is_rectification_notice: **true**

### 其它问题

**位置**：第三章节

**结构**：
```
1. 工点名称（检查时间）
   ⑴ 问题 1
   ⑵ 问题 2
   ⑶ 问题 3
   ...
```

**示例**：
```
1. 中铁二十五局施工，广西宁铁监理的QFSG2标冲仓中桥（检查时间2025年8月6日）
⑴施工中的3-2#桩基只剩下1根护桩，不能精准量测孔位中心偏差值，不符合《铁路桥梁钻孔桩施工技术规程》（Q/CR9212-2015）相关规定。
⑵泥浆池的沉淀池、制浆池间的隔离墙已被水淹没，泥浆漫流，未形成循环系统，不符合《铁路桥梁钻孔桩施工技术规程》（Q/CR9212-2015）4.4.2规定及施工方案的要求（图1）。
⑶0#桥台小里程端路基排水不畅通，淤泥泛滥，文明施工较差，防排水措施落实不到位（图2）。
```

**提取字段**：
- issue_number: 自动生成
- description: 从"⑴⑵⑶..."提取
- is_rectification_notice: **false**

---

## 🔄 解析流程

### 步骤 1：文档分段

```python
def parse_document(doc):
    """解析 Word 文档"""
    
    sections = {
        'header': [],
        'overview': [],
        'rectification_notices': [],
        'other_issues': [],
        'supervision_opinion': [],
        'attachments': []
    }
    
    current_section = 'header'
    
    for para in doc.paragraphs:
        text = para.text.strip()
        
        if "二、下发整改通知单" in text:
            current_section = 'rectification_notices'
        elif "三、存在的其它" in text:
            current_section = 'other_issues'
        elif "四、监督意见" in text:
            current_section = 'supervision_opinion'
        
        sections[current_section].append(text)
    
    return sections
```

### 步骤 2：提取下发整改通知单的问题

```python
def extract_rectification_notices(paragraphs):
    """提取下发整改通知单的问题"""
    
    issues = []
    current_issue = None
    
    for para in paragraphs:
        text = para.text.strip()
        
        # 识别工点（以数字开头）
        if text and text[0].isdigit() and '．' in text:
            if current_issue:
                issues.append(current_issue)
            
            current_issue = {
                'point_info': text,
                'check_situation': '',
                'handling_measures': '',
                'is_rectification_notice': True
            }
        
        # 提取检查情况
        elif text.startswith('检查情况：'):
            current_issue['check_situation'] = text.replace('检查情况：', '')
        
        # 提取处理措施
        elif text.startswith('处理措施：'):
            current_issue['handling_measures'] = text.replace('处理措施：', '')
    
    if current_issue:
        issues.append(current_issue)
    
    return issues
```

### 步骤 3：提取其它问题

```python
def extract_other_issues(paragraphs):
    """提取其它问题"""
    
    issues = []
    current_issue = None
    current_point = None
    
    for para in paragraphs:
        text = para.text.strip()
        
        # 识别工点（以数字开头）
        if text and text[0].isdigit() and '．' in text:
            current_point = text
        
        # 识别问题（以⑴⑵⑶等开头）
        elif text and text[0] in '⑴⑵⑶⑷⑸⑹⑺⑻⑼':
            issues.append({
                'point_info': current_point,
                'description': text,
                'is_rectification_notice': False
            })
    
    return issues
```

### 步骤 4：字段提取

```python
def extract_fields(issue_data):
    """从问题数据中提取字段"""
    
    import re
    
    # 提取工点名称
    point_name = extract_point_name(issue_data['point_info'])
    
    # 提取检查时间
    check_date = extract_date(issue_data['point_info'])
    
    # 提取整改通知单编号
    notice_number = None
    if '整改通知单' in issue_data.get('handling_measures', ''):
        match = re.search(r'（([^）]+)）', issue_data['handling_measures'])
        if match:
            notice_number = match.group(1)
    
    # 提取整改期限
    deadline = extract_date(issue_data.get('handling_measures', ''))
    
    # 提取处罚措施
    penalties = extract_penalties(issue_data.get('handling_measures', ''))
    
    return {
        'point_name': point_name,
        'check_date': check_date,
        'description': issue_data.get('check_situation') or issue_data.get('description'),
        'deadline': deadline,
        'penalties': penalties,
        'is_rectification_notice': issue_data['is_rectification_notice']
    }
```

---

## 🎯 关键提取规则

### 日期提取
```python
import re
from datetime import datetime

def extract_date(text):
    """从文本中提取日期"""
    
    # 匹配 YYYY年MM月DD日 格式
    match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', text)
    if match:
        year, month, day = match.groups()
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    
    return None
```

### 处罚措施提取
```python
def extract_penalties(text):
    """从文本中提取处罚措施"""
    
    penalties = []
    
    penalty_keywords = {
        '责令改正': 'rectification_order',
        '拆除返工': 'demolition_rework',
        '临时停工': 'temporary_suspension',
        '施工一般': 'construction_general',
        '施工较大': 'construction_major',
        '施工重大': 'construction_severe',
        '监理一般': 'supervision_general',
        '监理较大': 'supervision_major',
        '监理重大': 'supervision_severe'
    }
    
    for keyword, penalty_type in penalty_keywords.items():
        if keyword in text:
            penalties.append(penalty_type)
    
    return penalties
```

### 工点名称提取
```python
def extract_point_name(text):
    """从工点信息中提取工点名称"""
    
    # 示例：1．中铁三局施工，广西宁铁监理的QFSG1标皇马隧道出口（检查时间2025年8月7日）
    # 提取：QFSG1标皇马隧道出口
    
    import re
    
    # 查找"的"之后、"（"之前的内容
    match = re.search(r'的(.+?)（', text)
    if match:
        return match.group(1)
    
    return text
```

---

## 📊 数据库存储

### 下发整改通知单的问题

```sql
INSERT INTO issues (
  issue_number,
  description,
  rectification_measures,
  deadline,
  is_rectification_notice,
  is_bad_behavior_notice
) VALUES (
  '南宁站钦防二线〔2025〕（改字）06号',
  '用于隧道纵向施工缝的水泥基渗透结晶型防水涂料经查无进场验收记录，原材料未检先用。',
  '向施工单位下发《整改通知单》责令改正，2025年8月20日前完成整改，当期信用评价中扣1分。',
  '2025-08-20',
  true,
  false
);

INSERT INTO issue_penalties (issue_id, penalty_type) VALUES
  (1, 'rectification_order');
```

### 其它问题

```sql
INSERT INTO issues (
  issue_number,
  description,
  is_rectification_notice,
  is_bad_behavior_notice
) VALUES (
  'auto-generated',
  '施工中的3-2#桩基只剩下1根护桩，不能精准量测孔位中心偏差值，不符合《铁路桥梁钻孔桩施工技术规程》（Q/CR9212-2015）相关规定。',
  false,
  false
);
```

---

## ✅ 实现检查清单

- [ ] 实现文档分段识别
- [ ] 实现下发整改通知单章节识别
- [ ] 实现其它问题章节识别
- [ ] 实现工点信息提取
- [ ] 实现问题描述提取
- [ ] 实现日期提取
- [ ] 实现处罚措施提取
- [ ] 实现整改通知单编号提取
- [ ] 实现图片提取和关联
- [ ] 实现人工审核界面

---

**版本**：1.0

**最后更新**：2025-10-24


