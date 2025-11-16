# 前端导入确认界面修改方案

## 📋 概述

增强 `ImportConfirm.vue` 和 `ImportPreview.vue` 的功能，支持行内编辑、标段选择、问题类别筛选。

---

## 1️⃣ ImportPreview.vue 修改方案

### 1.1 显示字段列表

**显示的字段**（按优先级）：
```javascript
const displayFields = [
  { key: 'issue_number', label: '问题编号', width: 100, editable: false },
  { key: 'site_name', label: '工点', width: 120, editable: true },
  { key: 'section_name', label: '标段', width: 150, editable: true, type: 'select' },
  { key: 'description', label: '问题描述', width: 250, editable: true },
  { key: 'issue_category', label: '问题类别', width: 120, editable: true, type: 'select' },
  { key: 'severity', label: '严重程度', width: 100, editable: true, type: 'select' },
  { key: 'is_rectification_notice', label: '整改通知', width: 100, editable: true, type: 'checkbox' },
  { key: 'is_bad_behavior_notice', label: '不良行为', width: 100, editable: true, type: 'checkbox' },
  { key: 'inspection_unit', label: '检查单位', width: 120, editable: true },
  { key: 'inspection_date', label: '检查日期', width: 120, editable: true, type: 'date' },
  { key: 'inspection_personnel', label: '检查人员', width: 120, editable: true },
  { key: 'rectification_requirements', label: '整改要求', width: 200, editable: true },
  { key: 'rectification_deadline', label: '整改期限', width: 120, editable: true, type: 'date' },
  { key: 'responsible_unit', label: '责任单位', width: 120, editable: true },
  { key: 'responsible_person', label: '责任人', width: 100, editable: true }
]
```

### 1.2 行内编辑功能

**实现方式**：
```javascript
// 编辑状态管理
const editingCell = ref(null) // { rowIndex, fieldKey }
const editedValues = ref({})  // { rowIndex_fieldKey: value }

// 编辑处理
const startEdit = (rowIndex, fieldKey) => {
  editingCell.value = { rowIndex, fieldKey }
}

const saveEdit = (rowIndex, fieldKey, newValue) => {
  const key = `${rowIndex}_${fieldKey}`
  editedValues.value[key] = newValue
  importStore.updateRecognizedIssue(rowIndex, fieldKey, newValue)
  editingCell.value = null
}

const cancelEdit = () => {
  editingCell.value = null
}
```

### 1.3 标段下拉选择

**数据来源**：
```javascript
// 1. 本次识别结果中的标段
const recognizedSections = computed(() => {
  const sections = new Set()
  importStore.recognizedIssues.forEach(issue => {
    if (issue.section_name) sections.add(issue.section_name)
  })
  return Array.from(sections).sort()
})

// 2. 数据库中的标段（按项目筛选）
const dbSections = ref([])

const loadDbSections = async () => {
  try {
    const projectName = importStore.recognizedNotices[0]?.project_name
    if (projectName) {
      const response = await fetch(`/api/sections?project_name=${projectName}`)
      dbSections.value = await response.json()
    }
  } catch (error) {
    logger.error('Failed to load sections:', error)
  }
}

// 3. 合并选项
const sectionOptions = computed(() => {
  const options = new Set([...recognizedSections.value, ...dbSections.value.map(s => s.section_name)])
  return Array.from(options).sort()
})
```

### 1.4 问题类别筛选

**三层结构筛选**：
```javascript
// 问题类别树
const categoryTree = {
  '工程质量': {
    '混凝土工程': ['原材料', '模板及支架', '钢筋', ...],
    '路基工程': ['地基处理', '填料填筑', ...],
    ...
  },
  '施工安全': {
    '隧道施工': [],
    '脚手架、支架工程': [],
    ...
  },
  '管理行为': {
    '建设单位': ['管理制度', '资源配置', ...],
    ...
  }
}

// 筛选状态
const selectedCategory = ref(null)      // 一级分类
const selectedType1 = ref(null)         // 二级分类
const selectedType2 = ref(null)         // 三级分类

// 筛选逻辑
const filteredIssues = computed(() => {
  return importStore.recognizedIssues.filter(issue => {
    if (selectedCategory.value && issue.issue_category !== selectedCategory.value) return false
    if (selectedType1.value && issue.issue_type_level1 !== selectedType1.value) return false
    if (selectedType2.value && issue.issue_type_level2 !== selectedType2.value) return false
    return true
  })
})
```

---

## 2️⃣ ImportConfirm.vue 修改方案

### 2.1 显示选中问题的完整信息

**修改表格**：
```vue
<el-table :data="selectedIssues" stripe border max-height="400px">
  <el-table-column prop="issue_number" label="问题编号" width="100" />
  <el-table-column prop="site_name" label="工点" width="100" />
  <el-table-column prop="section_name" label="标段" width="150" />
  <el-table-column prop="description" label="问题描述" min-width="200" show-overflow-tooltip />
  <el-table-column prop="issue_category" label="问题类别" width="100" />
  <el-table-column prop="severity" label="严重程度" width="80" />
  <el-table-column prop="is_rectification_notice" label="整改通知" width="80">
    <template #default="{ row }">
      <el-tag :type="row.is_rectification_notice ? 'success' : 'info'">
        {{ row.is_rectification_notice ? '是' : '否' }}
      </el-tag>
    </template>
  </el-table-column>
</el-table>
```

### 2.2 快速编辑功能

**添加编辑按钮**：
```vue
<el-table-column label="操作" width="100" fixed="right">
  <template #default="{ row, $index }">
    <el-button link type="primary" @click="editIssue($index)">编辑</el-button>
  </template>
</el-table-column>

<!-- 编辑对话框 -->
<el-dialog v-model="editDialogVisible" title="编辑问题">
  <el-form :model="editingIssue" label-width="120px">
    <el-form-item label="标段">
      <el-select v-model="editingIssue.section_name" :options="sectionOptions" />
    </el-form-item>
    <el-form-item label="工点">
      <el-input v-model="editingIssue.site_name" />
    </el-form-item>
    <el-form-item label="问题描述">
      <el-input v-model="editingIssue.description" type="textarea" rows="3" />
    </el-form-item>
    <!-- 其他字段... -->
  </el-form>
  <template #footer>
    <el-button @click="editDialogVisible = false">取消</el-button>
    <el-button type="primary" @click="saveEdit">保存</el-button>
  </template>
</el-dialog>
```

---

## 3️⃣ importStore.js 修改方案

### 3.1 新增方法

```javascript
// 更新识别的问题
const updateRecognizedIssue = (index, fieldKey, value) => {
  if (recognizedIssues.value[index]) {
    recognizedIssues.value[index][fieldKey] = value
    modifiedRecords.value.add(index)
  }
}

// 获取数据库中的标段
const fetchSections = async (projectName) => {
  try {
    const response = await fetch(`/api/sections?project_name=${projectName}`)
    return await response.json()
  } catch (error) {
    logger.error('Failed to fetch sections:', error)
    return []
  }
}

// 验证问题数据
const validateIssue = (issue) => {
  const errors = []
  if (!issue.description) errors.push('问题描述不能为空')
  if (!issue.section_name) errors.push('标段名称不能为空')
  return errors
}

// 导入前验证所有选中问题
const validateSelectedIssues = () => {
  const errors = {}
  selectedIssueIds.value.forEach(index => {
    const issue = recognizedIssues.value[index]
    const issueErrors = validateIssue(issue)
    if (issueErrors.length > 0) {
      errors[index] = issueErrors
    }
  })
  return errors
}
```

### 3.2 修改 importSelected 方法

```javascript
const importSelected = async () => {
  // 验证
  const errors = validateSelectedIssues()
  if (Object.keys(errors).length > 0) {
    ElMessage.error('存在验证错误，请修正后重试')
    return false
  }
  
  // 构建请求数据
  const selectedIssues = recognizedIssues.value.filter((_, index) =>
    selectedIssueIds.value.has(index)
  )
  
  // 调用 API
  const result = await importService.importSelected(
    recognizedNotices.value[0],
    selectedIssues
  )
  
  // 处理结果
  if (result.success) {
    ElMessage.success(`成功导入 ${result.imported_issues_count} 个问题`)
    viewMode.value = 'result'
    return true
  } else {
    ElMessage.error(result.error)
    return false
  }
}
```

---

## 4️⃣ 后端 API 修改方案

### 4.1 新增 API 端点

```python
@app.get("/api/sections")
async def get_sections(project_name: str):
    """获取项目下的所有标段"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id, s.section_name
            FROM sections s
            JOIN projects p ON s.project_id = p.id
            WHERE p.project_name = ?
            ORDER BY s.section_name
        """, (project_name,))
        sections = [{'id': row[0], 'section_name': row[1]} for row in cursor.fetchall()]
        conn.close()
        return sections
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 4.2 修改 `/api/import/selected` 端点

**改变请求格式**：
```python
class ImportSelectedRequest(BaseModel):
    notice_data: Dict  # 通知书数据
    selected_issues: List[Dict]  # 直接传递完整的问题数据（包括用户编辑的内容）

@app.post("/api/import/selected")
async def import_selected(request: ImportSelectedRequest):
    """导入选中的问题"""
    try:
        service = ImportService(str(DB_PATH))
        result = service.import_selected_issues(
            request.notice_data,
            request.selected_issues  # 改为传递完整问题数据
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

## 5️⃣ 实施顺序

1. ⏳ 修改后端 `_insert_issue` 方法
2. ⏳ 修改后端 API 端点
3. ⏳ 修改 `importStore.js`
4. ⏳ 修改 `ImportPreview.vue`
5. ⏳ 修改 `ImportConfirm.vue`
6. ⏳ 测试完整流程

---

## 6️⃣ 测试清单

- [ ] 导入时能正确显示标段名称
- [ ] 能编辑标段名称
- [ ] 标段下拉选择正常工作
- [ ] 问题类别筛选正常工作
- [ ] 编辑后的数据能正确保存到数据库
- [ ] 现有问题查询功能不受影响


