# 导入流程问题修复 - 快速参考

## 🐛 问题
确认界面无数据，显示"No Data"

## 🔍 原因
编辑界面没有问题选择逻辑，`selectedIssueIds` 为空

## ✅ 修复

### 修改文件
`frontend/src/components/ImportIssuesEditor.vue`

### 修改内容

#### 1. 添加选择框列
```vue
<el-table-column type="selection" width="50" />
```

#### 2. 添加选择事件
```vue
@selection-change="handleSelectionChange"
```

#### 3. 添加处理方法
```javascript
const handleSelectionChange = (selection) => {
  importStore.selectedIssueIds.clear()
  selection.forEach((issue) => {
    const index = issues.value.indexOf(issue)
    if (index !== -1) {
      importStore.selectedIssueIds.add(index)
    }
  })
}
```

#### 4. 修改保存方法
```javascript
const handleSave = () => {
  if (importStore.selectedIssueIds.size === 0) {
    ElMessage.warning('请先选择要导入的问题')
    return
  }
  ElMessage.success('修改已保存')
  importStore.viewMode = 'confirm'
}
```

#### 5. 添加计数
```javascript
const selectedCount = computed(() => {
  return importStore.selectedIssueIds.size
})
```

## 🎯 效果

- ✅ 编辑界面显示选择框
- ✅ 用户可以选择问题
- ✅ 统计信息显示已选择数
- ✅ 确认界面显示选中的问题

## 🧪 快速测试

```bash
# 1. 启动应用
./start-dev.sh

# 2. 上传文档 → 识别 → 编辑界面

# 3. 验证
# ✅ 表格显示选择框
# ✅ 选择问题
# ✅ 统计信息显示已选择数
# ✅ 保存后进入确认界面
# ✅ 确认界面显示选中的问题
```

## 📝 修改统计

| 指标 | 数值 |
|------|------|
| 修改的文件数 | 1 |
| 新增的列 | 1 |
| 新增的方法 | 1 |
| 修改的方法 | 1 |
| 新增的计算属性 | 1 |

---

**版本**：1.0
**日期**：2025-11-15

