# 🎯 下发整改通知单问题识别规范

## 📋 核心需求

应用需要能够**自动识别和区分**：
1. ✅ **下发整改通知单的问题** - 已下发整改通知单，需要立即整改
2. ❌ **其它安全质量问题** - 未下发整改通知单，仅作为监督意见

---

## 🔍 识别方法

### 方法 1：基于文档章节位置

#### 监督通知书的标准结构

```
二、下发整改通知单的工点及问题
   ↓
   这一章节中的所有问题
   is_rectification_notice = TRUE

三、存在的其它主要安全质量等问题
   ↓
   这一章节中的所有问题
   is_rectification_notice = FALSE
```

#### 识别规则

| 章节标题 | 关键词 | is_rectification_notice |
|--------|--------|----------------------|
| 二、下发整改通知单 | "二、下发整改通知单" | **true** |
| 三、存在的其它 | "三、存在的其它" | **false** |
| 四、监督意见 | "四、监督意见" | 不作为问题 |

### 方法 2：基于处理措施关键词

#### 下发整改通知单的特征

```
处理措施中包含以下关键词：
- "下发《整改通知单》"
- "整改通知单"
- "改字"（如：〔2025〕（改字）06号）
- "责令改正"
- "限期整改"
```

#### 其它问题的特征

```
处理措施中包含以下关键词：
- "要求"
- "建议"
- "应该"
- "需要"
- "不符合"
- "存在隐患"
```

### 方法 3：基于整改通知单编号

#### 整改通知单编号格式

```
南宁站钦防二线〔2025〕（改字）06号
├─ 南宁站 - 监督站名称
├─ 钦防二线 - 项目名称
├─ 〔2025〕 - 年份
├─ （改字） - 类型标识 ⭐ 关键
└─ 06号 - 序号
```

**识别规则**：
- 如果编号中包含 `（改字）` 或 `（通知）` → **is_rectification_notice = true**
- 如果没有编号 → **is_rectification_notice = false**

---

## 🔄 识别流程

### 步骤 1：文档分段

```python
def parse_supervision_notice(doc):
    """解析监督通知书"""
    
    sections = {
        'rectification_notices': [],  # 下发整改通知单的问题
        'other_issues': []             # 其它问题
    }
    
    current_section = None
    
    for para in doc.paragraphs:
        text = para.text.strip()
        
        # 识别章节
        if "二、下发整改通知单" in text:
            current_section = 'rectification_notices'
            continue
        
        elif "三、存在的其它" in text:
            current_section = 'other_issues'
            continue
        
        elif "四、监督意见" in text:
            current_section = None
            continue
        
        # 添加到对应章节
        if current_section and text:
            sections[current_section].append(text)
    
    return sections
```

### 步骤 2：提取问题

```python
def extract_issues(sections):
    """从各章节提取问题"""
    
    issues = []
    
    # 提取下发整改通知单的问题
    for issue_data in extract_rectification_notices(sections['rectification_notices']):
        issue_data['is_rectification_notice'] = True
        issues.append(issue_data)
    
    # 提取其它问题
    for issue_data in extract_other_issues(sections['other_issues']):
        issue_data['is_rectification_notice'] = False
        issues.append(issue_data)
    
    return issues
```

### 步骤 3：验证识别结果

```python
def verify_rectification_notice(issue_data):
    """验证识别结果"""
    
    # 方法 1：检查章节位置
    if issue_data.get('document_section') == 'rectification':
        return True
    
    # 方法 2：检查处理措施中的关键词
    handling_measures = issue_data.get('handling_measures', '')
    if '下发《整改通知单》' in handling_measures or '整改通知单' in handling_measures:
        return True
    
    # 方法 3：检查整改通知单编号
    if issue_data.get('notice_number') and '（改字）' in issue_data['notice_number']:
        return True
    
    return False
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
  document_section,
  document_source
) VALUES (
  '南宁站钦防二线〔2025〕（改字）06号',
  '用于隧道纵向施工缝的水泥基渗透结晶型防水涂料经查无进场验收记录，原材料未检先用。',
  '向施工单位下发《整改通知单》（南宁站钦防二线〔2025〕（改字）06号）责令改正，2025年8月20日前完成整改，当期信用评价中扣1分。',
  '2025-08-20',
  true,
  'rectification',
  'word'
);
```

### 其它问题

```sql
INSERT INTO issues (
  issue_number,
  description,
  is_rectification_notice,
  document_section,
  document_source
) VALUES (
  'auto-generated',
  '施工中的3-2#桩基只剩下1根护桩，不能精准量测孔位中心偏差值，不符合《铁路桥梁钻孔桩施工技术规程》（Q/CR9212-2015）相关规定。',
  false,
  'other',
  'word'
);
```

---

## 🎯 前端展示

### 列表视图

```
【下发整改通知单的问题】
┌─────────────────────────────────────────────────────┐
│ 编号: 南宁站钦防二线〔2025〕（改字）06号            │
│ 工点: QFSG1标皇马隧道出口                           │
│ 问题: 水泥基渗透结晶型防水涂料无进场验收记录...     │
│ 期限: 2025-08-20                                    │
│ 状态: ⭐ 已下发整改通知单                           │
└─────────────────────────────────────────────────────┘

【其它问题】
┌─────────────────────────────────────────────────────┐
│ 工点: QFSG2标冲仓中桥                               │
│ 问题: 施工中的3-2#桩基只剩下1根护桩...              │
│ 状态: 监督意见                                      │
└─────────────────────────────────────────────────────┘
```

### 统计视图

```
【问题统计】
├─ 总问题数: 30
├─ 下发整改通知单: 1 ⭐
└─ 其它问题: 29

【按类型统计】
├─ 质量问题: 9
├─ 安全问题: 6
└─ 管理问题: 15
```

---

## 🔧 实现建议

### Phase 1：基础识别
- ✅ 实现文档分段识别
- ✅ 基于章节位置识别
- ✅ 提取整改通知单编号

### Phase 2：增强识别
- ⭐ 基于关键词识别
- ⭐ 验证识别结果
- ⭐ 处理边界情况

### Phase 3：人工审核
- 📋 提供人工审核界面
- 📋 支持修改识别结果
- 📋 记录修改历史

---

## ✅ 测试用例

### 测试 1：标准下发整改通知单

```
输入：
  章节: "二、下发整改通知单的工点及问题"
  处理措施: "向施工单位下发《整改通知单》（南宁站钦防二线〔2025〕（改字）06号）"

预期输出：
  is_rectification_notice: true
  document_section: 'rectification'
```

### 测试 2：其它问题

```
输入：
  章节: "三、存在的其它主要安全质量等问题"
  描述: "施工中的3-2#桩基只剩下1根护桩..."

预期输出：
  is_rectification_notice: false
  document_section: 'other'
```

### 测试 3：边界情况

```
输入：
  处理措施: "要求建设单位组织参建各方现场勘察，优化方案"

预期输出：
  is_rectification_notice: false
```

---

## 📈 关键指标

| 指标 | 目标 |
|------|------|
| 识别准确率 | ≥ 95% |
| 误识别率 | ≤ 5% |
| 漏识别率 | ≤ 5% |
| 处理速度 | < 1 秒/文档 |

---

**版本**：1.0

**最后更新**：2025-10-24


