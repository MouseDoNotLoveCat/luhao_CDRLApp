# 问题类别导入错误 - 修复总结

## 🐛 问题描述

用户在编辑界面修改问题类型后（例如：质量问题-隧道工程，管理问题-设计单位-管理体系），点击导入到数据库时，所有问题的类型都被错误地写入为"施工安全"。

## 🔍 根本原因分析

### 问题链路
1. **前端编辑** ✅ 用户在 `ImportIssuesEditor.vue` 中修改问题类别
2. **状态保存** ✅ 修改保存到 `recognizedIssues` 状态
3. **数据传递** ❌ **问题1**：编辑后的完整问题数据没有传递到后端
4. **后端处理** ❌ **问题2**：后端 `_insert_issue` 方法总是使用分类器重新分类，覆盖用户编辑的值
5. **数据库保存** ❌ **问题3**：INSERT 语句没有包含 `issue_type_level1` 和 `issue_type_level2` 字段

## ✅ 修复方案

### 1. 前端修改 - `importStore.js`

**修改内容**：`importSelected` 方法
- 从 `recognizedIssues` 中提取选中的完整问题数据
- 将完整问题数据（包括用户编辑的 `issue_category`, `issue_type_level1`, `issue_type_level2`）传递到后端
- 更新 `noticeData.issues` 为选中的问题列表

**关键代码**：
```javascript
const selectedIssues = recognizedIssues.value.filter((_, index) =>
  selectedIssueIds.value.has(index)
)
const updatedNoticeData = {
  ...noticeData,
  issues: selectedIssues
}
```

### 2. 后端 API 修改 - `main.py`

**修改内容**：`ImportSelectedRequest` 模型
- 更新注释说明 `notice_data` 包含完整的问题数据
- 更新注释说明 `selected_issue_ids` 是问题索引列表

### 3. 后端导入服务修改 - `import_service.py`

**修改内容1**：`_insert_issue` 方法的问题类别处理
- 优先使用用户编辑的 `issue_category`
- 只在为空时才使用自动分类器
- 添加日志记录问题类别来源

**修改内容2**：INSERT 语句
- 添加 `issue_type_level1` 和 `issue_type_level2` 字段
- 从问题数据中获取这两个字段的值

**关键代码**：
```python
# 优先使用用户编辑的问题类别
issue_category = issue.get('issue_category')

if not issue_category:
    # 只在为空时才使用自动分类
    issue_category = IssueCategoryClassifier.classify(...)
    if not issue_category or issue_category == '其它':
        issue_category = '施工安全'
```

## 📊 修改文件清单

| 文件 | 修改内容 | 状态 |
|------|--------|------|
| `frontend/src/stores/importStore.js` | 修改 `importSelected` 方法，传递完整问题数据 | ✅ |
| `backend/app/main.py` | 更新 `ImportSelectedRequest` 模型注释 | ✅ |
| `backend/app/services/import_service.py` | 修改 `_insert_issue` 方法，优先使用用户编辑值 | ✅ |
| `backend/app/services/import_service.py` | 修改 INSERT 语句，包含三层分类字段 | ✅ |

## 🧪 测试步骤

1. **启动应用**
   ```bash
   ./start-dev.sh
   ```

2. **上传 Word 文档**
   - 进入导入页面
   - 上传包含多个问题的 Word 文档

3. **进入编辑界面**
   - 点击"编辑问题"按钮
   - 修改至少 2 个问题的类别

4. **验证修改**
   - 修改问题1：质量问题 → 隧道工程
   - 修改问题2：管理问题 → 设计单位 → 管理体系

5. **导入数据库**
   - 选择修改过的问题
   - 点击"下一步"进入确认界面
   - 点击"保存到数据库"

6. **验证结果**
   - 查看数据库中的问题记录
   - 确认 `issue_category`, `issue_type_level1`, `issue_type_level2` 都是用户编辑的值
   - 不应该被默认值"施工安全"覆盖

## 📝 预期效果

- ✅ 用户编辑的问题类别能正确保存到数据库
- ✅ 三层问题分类都能正确保存
- ✅ 不会被自动分类器的默认值覆盖
- ✅ 日志中显示问题类别来源（用户编辑或自动分类）

## 🔄 数据流图

```
编辑界面修改
    ↓
recognizedIssues 状态更新
    ↓
用户点击导入
    ↓
importSelected 方法
    ↓
提取选中的完整问题数据 ← 关键修改
    ↓
传递到后端 API
    ↓
_insert_issue 方法
    ↓
优先使用用户编辑的值 ← 关键修改
    ↓
INSERT 语句包含三层分类 ← 关键修改
    ↓
数据库保存
```

## ✨ 关键改进

1. **数据完整性**：完整的问题数据从前端传递到后端
2. **优先级正确**：用户编辑的值优先于自动分类
3. **字段完整**：三层问题分类都能保存
4. **可追踪性**：日志记录问题类别来源

---

**修复状态**：✅ 完成
**最后更新**：2025-11-15
**版本**：1.0

