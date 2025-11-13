# 🎯 下发整改通知单问题识别实现方案

## 📋 需求总结

应用需要能够**自动识别和区分**监督通知书中的两类问题：

1. **下发整改通知单的问题** ⭐
   - 位置：第二章节"二、下发整改通知单的工点及问题"
   - 特征：已下发整改通知单，需要立即整改
   - 标记：`is_rectification_notice = true`

2. **其它安全质量问题**
   - 位置：第三章节"三、存在的其它主要安全质量等问题"
   - 特征：未下发整改通知单，仅作为监督意见
   - 标记：`is_rectification_notice = false`

---

## 🔍 识别方法

### 方法 1：基于文档章节位置（推荐）

**优点**：准确率最高（95%+），实现简单

**实现**：
```python
def identify_by_section(doc):
    """基于文档章节位置识别"""
    
    current_section = None
    issues = []
    
    for para in doc.paragraphs:
        text = para.text.strip()
        
        # 识别章节
        if "二、下发整改通知单" in text:
            current_section = 'rectification'
        elif "三、存在的其它" in text:
            current_section = 'other'
        elif "四、监督意见" in text:
            current_section = None
        
        # 提取问题
        if current_section and is_issue(text):
            issue = parse_issue(text)
            issue['is_rectification_notice'] = (current_section == 'rectification')
            issues.append(issue)
    
    return issues
```

### 方法 2：基于处理措施关键词

**优点**：可作为验证方法

**关键词**：
- 下发整改通知单：`"下发《整改通知单》"`, `"整改通知单"`, `"（改字）"`
- 其它问题：`"要求"`, `"建议"`, `"应该"`, `"需要"`

### 方法 3：基于整改通知单编号

**优点**：可作为二次验证

**编号格式**：`南宁站钦防二线〔2025〕（改字）06号`

**识别规则**：
- 包含 `（改字）` 或 `（通知）` → 下发整改通知单
- 无编号 → 其它问题

---

## 🗄️ 数据库设计

### 新增字段

在 `issues` 表中新增两个字段：

```sql
-- 文档章节标识
document_section VARCHAR(50),  -- 'rectification' 或 'other'

-- 数据来源标识
document_source VARCHAR(50),   -- 'excel' 或 'word'
```

### 关键字段说明

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| is_rectification_notice | Boolean | 是否下发整改通知单 | true/false |
| document_section | String | 文档章节 | 'rectification'/'other' |
| document_source | String | 数据来源 | 'excel'/'word' |
| issue_number | String | 隐患编号 | '南宁站钦防二线〔2025〕（改字）06号' |

---

## 📥 导入流程

### Word 文档导入流程

```
1. 上传 Word 文档
   ↓
2. 解析文档结构
   ├─ 识别"二、下发整改通知单"章节
   └─ 识别"三、存在的其它"章节
   ↓
3. 提取问题信息
   ├─ 工点名称、检查时间
   ├─ 问题描述
   ├─ 处理措施、整改期限
   └─ 整改通知单编号
   ↓
4. 标记问题类型
   ├─ is_rectification_notice = true (第二章节)
   └─ is_rectification_notice = false (第三章节)
   ↓
5. 数据验证
   ├─ 验证必填字段
   ├─ 验证日期格式
   └─ 验证编号格式
   ↓
6. 保存到数据库
   ↓
7. 生成导入报告
```

---

## 📊 数据示例

### 下发整改通知单的问题

```
【原始文档】
二、下发整改通知单的工点及问题
1．中铁三局施工，广西宁铁监理的QFSG1标皇马隧道出口（检查时间2025年8月7日）
检查情况：用于隧道纵向施工缝的水泥基渗透结晶型防水涂料经查无进场验收记录，原材料未检先用。
处理措施：向施工单位下发《整改通知单》（南宁站钦防二线〔2025〕（改字）06号）责令改正，2025年8月20日前完成整改，当期信用评价中扣1分。

【数据库存储】
{
  "issue_number": "南宁站钦防二线〔2025〕（改字）06号",
  "point_name": "QFSG1标皇马隧道出口",
  "inspection_date": "2025-08-07",
  "description": "用于隧道纵向施工缝的水泥基渗透结晶型防水涂料经查无进场验收记录，原材料未检先用。",
  "rectification_measures": "向施工单位下发《整改通知单》（南宁站钦防二线〔2025〕（改字）06号）责令改正，2025年8月20日前完成整改，当期信用评价中扣1分。",
  "deadline": "2025-08-20",
  "is_rectification_notice": true,
  "document_section": "rectification",
  "document_source": "word"
}
```

### 其它问题

```
【原始文档】
三、存在的其它主要安全质量等问题
1. 中铁二十五局施工，广西宁铁监理的QFSG2标冲仓中桥（检查时间2025年8月6日）
⑴施工中的3-2#桩基只剩下1根护桩，不能精准量测孔位中心偏差值，不符合《铁路桥梁钻孔桩施工技术规程》（Q/CR9212-2015）相关规定。

【数据库存储】
{
  "issue_number": "auto-generated",
  "point_name": "QFSG2标冲仓中桥",
  "inspection_date": "2025-08-06",
  "description": "施工中的3-2#桩基只剩下1根护桩，不能精准量测孔位中心偏差值，不符合《铁路桥梁钻孔桩施工技术规程》（Q/CR9212-2015）相关规定。",
  "is_rectification_notice": false,
  "document_section": "other",
  "document_source": "word"
}
```

---

## 🎯 前端展示

### 问题列表视图

```
【下发整改通知单的问题】 (1 个)
┌─────────────────────────────────────────────────────┐
│ ⭐ 编号: 南宁站钦防二线〔2025〕（改字）06号        │
│    工点: QFSG1标皇马隧道出口                        │
│    问题: 水泥基渗透结晶型防水涂料无进场验收记录... │
│    期限: 2025-08-20                                 │
│    状态: 已下发整改通知单                           │
└─────────────────────────────────────────────────────┘

【其它问题】 (29 个)
┌─────────────────────────────────────────────────────┐
│    工点: QFSG2标冲仓中桥                            │
│    问题: 施工中的3-2#桩基只剩下1根护桩...          │
│    状态: 监督意见                                   │
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

## 🔧 实现步骤

### Phase 1：基础识别（第 2-3 周）
- [ ] 实现文档分段识别
- [ ] 基于章节位置识别
- [ ] 提取整改通知单编号
- [ ] 保存识别结果到数据库

### Phase 2：增强识别（第 3-4 周）
- [ ] 基于关键词验证
- [ ] 处理边界情况
- [ ] 提高识别准确率

### Phase 3：人工审核（第 4-5 周）
- [ ] 提供人工审核界面
- [ ] 支持修改识别结果
- [ ] 记录修改历史

---

## ✅ 验证方法

### 单元测试

```python
def test_rectification_notice_identification():
    """测试下发整改通知单识别"""
    
    # 测试 1：标准下发整改通知单
    doc = load_document("test_rectification.docx")
    issues = identify_issues(doc)
    assert issues[0]['is_rectification_notice'] == True
    
    # 测试 2：其它问题
    doc = load_document("test_other_issues.docx")
    issues = identify_issues(doc)
    assert issues[0]['is_rectification_notice'] == False
    
    # 测试 3：混合问题
    doc = load_document("test_mixed.docx")
    issues = identify_issues(doc)
    assert sum(1 for i in issues if i['is_rectification_notice']) == 1
    assert sum(1 for i in issues if not i['is_rectification_notice']) == 29
```

### 集成测试

```python
def test_import_workflow():
    """测试导入工作流"""
    
    # 上传文档
    response = upload_document("内部监督通知书钦防二线2025-08.docx")
    assert response.status_code == 200
    
    # 验证识别结果
    issues = get_issues()
    rectification_issues = [i for i in issues if i['is_rectification_notice']]
    other_issues = [i for i in issues if not i['is_rectification_notice']]
    
    assert len(rectification_issues) == 1
    assert len(other_issues) == 29
```

---

## 📈 关键指标

| 指标 | 目标 | 说明 |
|------|------|------|
| 识别准确率 | ≥ 95% | 正确识别的问题数 / 总问题数 |
| 误识别率 | ≤ 5% | 错误识别的问题数 / 总问题数 |
| 漏识别率 | ≤ 5% | 未识别的问题数 / 总问题数 |
| 处理速度 | < 1 秒 | 单个文档的处理时间 |

---

## 📚 相关文档

- **WORD_DOCUMENT_PARSING_GUIDE.md** - Word 文档解析指南
- **RECTIFICATION_NOTICE_IDENTIFICATION.md** - 识别规范详解
- **DATABASE_SCHEMA_COMPLETE.md** - 数据库设计（已更新）
- **README.md** - 项目规划（已更新）

---

**版本**：1.0

**最后更新**：2025-10-24

**状态**：✅ 完成


