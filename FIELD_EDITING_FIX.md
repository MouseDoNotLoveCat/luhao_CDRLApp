# 问题字段编辑功能实现

## 问题描述

### 原始需求
用户需要在导入流程中能够编辑识别出的问题字段，以修正识别错误的数据。

### 实现位置纠正
**初始错误实现**：字段编辑功能被错误地添加到了"问题确认界面"（`ImportConfirm.vue`）

**正确实现**：
1. **问题编辑界面**（`ImportIssuesEditor.vue`）- 应该在这里实现所有字段的编辑功能
2. **问题确认界面**（`ImportConfirm.vue`）- 只保留项目名称修改功能，其他字段只读显示

## 正确的工作流程

```
1. 上传文档 → 识别
   ↓
2. 预览通知书信息
   ↓
3. 【问题编辑界面】← 在这里编辑所有字段
   - 选择要导入的问题
   - 编辑施工单位、监理单位、工点、问题描述等
   - 编辑检查信息、整改信息、责任信息
   - 点击"保存修改"
   ↓
4. 【问题确认界面】← 只读显示，只能修改项目名称
   - 查看选中的问题列表（只读）
   - 修改项目-标段映射（通过 ProjectSectionMapping 组件）
   - 点击"确认导入"或"返回修改"
   ↓
5. 导入完成
```

## 修复内容

### 1. ImportIssuesEditor.vue（问题编辑界面）

**已有的可编辑字段**：
- ✅ 标段名称（下拉选择 + 可输入）
- ✅ 施工单位
- ✅ 监理单位
- ✅ 工点名称
- ✅ 问题描述（多行文本）
- ✅ 问题类别（三级级联选择）
- ✅ 严重程度（下拉选择）

**新增的可编辑字段**：
- ✅ 检查单位
- ✅ 检查人员
- ✅ 整改要求（多行文本）
- ✅ 整改期限
- ✅ 责任单位
- ✅ 责任人

**只读字段**：
- 检查时间（日期格式化显示）

### 2. ImportConfirm.vue（问题确认界面）

**恢复为只读显示**：
- 施工单位、监理单位
- 工点名称、问题描述
- 检查单位、检查人员、检查时间
- 整改要求、整改期限
- 责任单位、责任人

**保留的可编辑功能**：
- ✅ 项目名称修改（通过 ProjectSectionMapping 组件）
- ✅ 批量修改项目（通过 ProjectSectionMapping 组件）

**保留的操作按钮**：
- "返回修改" - 返回到问题编辑界面
- "取消导入" - 取消整个导入流程
- "确认导入" - 提交数据到后端

## 代码示例

### ImportIssuesEditor.vue - 可编辑字段示例

**单行文本字段**：
```vue
<el-table-column label="施工单位" width="150">
  <template #default="{ row, $index }">
    <el-input
      :model-value="row.contractor"
      @change="(val) => updateIssue($index, 'contractor', val)"
      placeholder="输入施工单位"
      size="small"
    />
  </template>
</el-table-column>
```

**多行文本字段**：
```vue
<el-table-column label="问题描述" width="200">
  <template #default="{ row, $index }">
    <el-input
      :model-value="row.description"
      @change="(val) => updateIssue($index, 'description', val)"
      type="textarea"
      :rows="2"
      placeholder="输入问题描述"
      size="small"
    />
  </template>
</el-table-column>
```

**更新函数**：
```javascript
// 更新问题字段
const updateIssue = (index, fieldName, value) => {
  importStore.updateRecognizedIssue(index, fieldName, value)
}
```

### ImportConfirm.vue - 只读显示示例

**只读文本显示**：
```vue
<el-table-column prop="contractor" label="施工单位" width="160" show-overflow-tooltip>
  <template #default="{ row }">
    {{ row.contractor || '未知施工单位' }}
  </template>
</el-table-column>
```

**项目名称显示**（通过映射计算）：
```vue
<el-table-column label="项目名称" width="150" show-overflow-tooltip>
  <template #default="{ row }">
    {{ getProjectName(row.section_name) }}
  </template>
</el-table-column>
```

## 用户体验

### 问题编辑界面（ImportIssuesEditor.vue）
**功能**：
- 用户可以自由编辑所有字段
- 支持批量选择问题
- 实时显示已选择和已修改的统计信息
- 点击"保存修改"进入确认界面

**优势**：
- 集中编辑，效率高
- 可以在导入前修正所有识别错误
- 修改会自动保存到 store

### 问题确认界面（ImportConfirm.vue）
**功能**：
- 只读显示所有字段，确保数据一致性
- 只允许修改项目-标段映射
- 提供"返回修改"按钮，可以返回编辑界面

**优势**：
- 清晰的确认流程，避免误操作
- 项目名称修改独立出来，逻辑清晰
- 如需修改其他字段，可以返回编辑界面

## 测试建议

### 测试问题编辑界面

1. **上传文档并进入编辑界面**：
   - 上传玉岑铁路或柳梧铁路监督通知书
   - 进入问题编辑界面

2. **测试基本字段编辑**：
   - 修改施工单位、监理单位
   - 修改工点名称
   - 修改问题描述（多行文本）

3. **测试新增字段编辑**：
   - 修改检查单位、检查人员
   - 修改整改要求（多行文本）
   - 修改整改期限
   - 修改责任单位、责任人

4. **测试问题选择**：
   - 选择部分问题
   - 验证统计信息更新

5. **保存并进入确认界面**：
   - 点击"保存修改"
   - 验证进入确认界面

### 测试问题确认界面

1. **验证只读显示**：
   - 确认所有字段都是只读显示
   - 确认无法直接编辑字段

2. **测试项目名称修改**：
   - 使用 ProjectSectionMapping 组件修改项目
   - 验证项目名称更新

3. **测试返回修改**：
   - 点击"返回修改"按钮
   - 验证返回到编辑界面
   - 验证之前的修改保留

4. **测试确认导入**：
   - 点击"确认导入"
   - 验证数据成功导入
   - 在问题列表中查看导入的数据

## 相关文件

### 修改的文件
1. **frontend/src/components/ImportIssuesEditor.vue**
   - 新增字段：检查单位、检查人员、整改要求、整改期限、责任单位、责任人
   - 位置：第 167-259 行

2. **frontend/src/components/ImportConfirm.vue**
   - 恢复所有字段为只读显示
   - 移除 `handleFieldUpdate` 函数
   - 保留项目名称修改功能

### 相关 Store
- **frontend/src/stores/importStore.js**
  - `updateRecognizedIssue()` 方法：第 447-452 行
  - `recognizedIssues` 状态
  - `selectedIssueIds` 状态
  - `modifiedRecords` 状态

## 注意事项

1. **数据流向**：
   - 编辑界面的修改 → store.recognizedIssues
   - 确认界面只读取 store.recognizedIssues
   - 导入时提交 store.recognizedIssues 到后端

2. **索引一致性**：
   - 编辑界面使用数组索引直接更新
   - 确认界面使用过滤后的数据显示

3. **修改追踪**：
   - 所有修改都会记录在 `modifiedRecords` 中
   - 编辑界面显示已修改数量

4. **工作流程清晰**：
   - 编辑 → 确认 → 导入
   - 确认界面提供"返回修改"功能
   - 避免在确认阶段进行复杂编辑

## 后续优化建议

1. **字段验证**：
   - 在编辑界面添加必填字段验证
   - 添加格式验证（日期、数字等）

2. **批量编辑**：
   - 选择多个问题
   - 批量修改相同字段

3. **编辑历史**：
   - 记录编辑历史
   - 支持撤销/重做

4. **自动保存**：
   - 定时自动保存编辑内容
   - 避免数据丢失

5. **变更高亮**：
   - 在确认界面高亮显示已修改的字段
   - 提供修改摘要

