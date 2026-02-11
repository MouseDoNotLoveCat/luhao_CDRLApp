# 问题编辑界面字段输入修复

## 问题描述

### 现象
在 `ImportIssuesEditor.vue`（问题编辑界面）中，虽然输入框显示出来了，但所有字段都无法编辑：
- 输入框可见但无法输入内容
- 下拉选择框无法选择
- 文本域无法输入

### 根本原因
使用了错误的 Vue 3 绑定语法：
- 使用了 `:model-value` 和 `@change` 的组合
- 这种组合在 Element Plus 的 `el-input` 中不会正确工作
- `@change` 事件只在失去焦点时触发，而且不会实时更新显示
- 导致输入框看起来是只读的

## 修复方案

### 正确的绑定方式

**对于 `el-input` 组件**：
- 使用 `v-model` 进行双向绑定
- 使用 `@input` 事件（而不是 `@change`）来触发更新
- `@input` 会在每次输入时立即触发，提供实时反馈

**对于 `el-select` 组件**：
- 使用 `v-model` 进行双向绑定
- 使用 `@change` 事件来触发更新
- `@change` 在选择改变时触发，这对下拉框是正确的

### 修复前后对比

**修复前（错误）**：
```vue
<!-- el-input - 无法输入 -->
<el-input
  :model-value="row.contractor"
  @change="(val) => updateIssue($index, 'contractor', val)"
  placeholder="输入施工单位"
  size="small"
/>

<!-- el-select - 无法选择 -->
<el-select
  :model-value="row.severity"
  @change="(val) => updateIssue($index, 'severity', val)"
  placeholder="选择严重程度"
  size="small"
>
  <el-option label="1 - 轻微" :value="1" />
</el-select>
```

**修复后（正确）**：
```vue
<!-- el-input - 可以输入 -->
<el-input
  v-model="row.contractor"
  @input="updateIssue($index, 'contractor', row.contractor)"
  placeholder="输入施工单位"
  size="small"
/>

<!-- el-select - 可以选择 -->
<el-select
  v-model="row.severity"
  @change="updateIssue($index, 'severity', row.severity)"
  placeholder="选择严重程度"
  size="small"
>
  <el-option label="1 - 轻微" :value="1" />
</el-select>
```

## 修复的字段

### 单行文本输入字段（使用 `v-model` + `@input`）
1. ✅ 施工单位 (`contractor`)
2. ✅ 监理单位 (`supervisor`)
3. ✅ 工点名称 (`site_name`)
4. ✅ 检查单位 (`inspection_unit`)
5. ✅ 检查人员 (`inspection_personnel`)
6. ✅ 整改期限 (`rectification_deadline`)
7. ✅ 责任单位 (`responsible_unit`)
8. ✅ 责任人 (`responsible_person`)

### 多行文本输入字段（使用 `v-model` + `@input`）
1. ✅ 问题描述 (`description`)
2. ✅ 整改要求 (`rectification_requirements`)

### 下拉选择字段（使用 `v-model` + `@change`）
1. ✅ 标段名称 (`section_name`) - 可输入的下拉框
2. ✅ 问题类别 (`issue_category`) - 一级分类
3. ✅ 问题子类1 (`issue_type_level1`) - 二级分类
4. ✅ 问题子类2 (`issue_type_level2`) - 三级分类
5. ✅ 严重程度 (`severity`)

### 只读字段（保持不变）
- 检查时间 (`inspection_date`) - 日期格式化显示

## 技术说明

### 为什么 `v-model` + `@input` 是正确的？

1. **`v-model` 提供双向绑定**：
   - 自动将输入值绑定到数据
   - 当数据变化时自动更新显示

2. **`@input` 提供实时更新**：
   - 每次输入都会触发
   - 可以立即调用 `updateIssue` 保存到 store
   - 用户可以看到实时反馈

3. **为什么不用 `@change`？**：
   - `@change` 只在失去焦点时触发
   - 用户输入时看不到反馈
   - 感觉像是只读的

### 为什么 `el-select` 使用 `@change`？

对于下拉选择框，`@change` 是正确的：
- 选择改变时立即触发
- 不需要失去焦点
- 符合下拉框的交互习惯

## 测试验证

### 测试步骤

1. **上传文档并进入编辑界面**：
   - 上传玉岑铁路或柳梧铁路监督通知书
   - 进入问题编辑界面

2. **测试单行文本输入**：
   - 点击"施工单位"输入框
   - 输入文字，验证可以正常输入
   - 修改"监理单位"、"工点名称"等字段
   - 验证所有单行文本字段都可以编辑

3. **测试多行文本输入**：
   - 点击"问题描述"文本域
   - 输入多行文字，包含换行
   - 验证可以正常输入和换行
   - 测试"整改要求"字段

4. **测试下拉选择**：
   - 点击"标段名称"下拉框
   - 选择一个标段或输入新标段
   - 测试"问题类别"三级级联选择
   - 测试"严重程度"下拉选择

5. **测试数据保存**：
   - 修改多个字段
   - 查看统计信息中的"已修改"数量
   - 点击"保存修改"进入确认界面
   - 验证修改的数据正确显示

## 相关文件

- **修复文件**：`frontend/src/components/ImportIssuesEditor.vue`
- **修复位置**：
  - 标段名称：第 33-53 行
  - 施工单位、监理单位、工点：第 56-90 行
  - 问题描述：第 101-113 行
  - 问题类别、严重程度：第 115-184 行
  - 检查单位、检查人员：第 186-208 行
  - 整改要求、整改期限：第 210-234 行
  - 责任单位、责任人：第 236-258 行

## 注意事项

1. **`v-model` vs `:model-value`**：
   - `v-model` 是 `:model-value` + `@update:modelValue` 的语法糖
   - 在表单控件中应该优先使用 `v-model`

2. **`@input` vs `@change`**：
   - `@input`：每次输入都触发（实时）
   - `@change`：失去焦点时触发（延迟）
   - 对于文本输入，使用 `@input` 提供更好的用户体验

3. **响应式更新**：
   - 使用 `v-model` 后，`row` 对象会自动更新
   - 在 `@input` 或 `@change` 中调用 `updateIssue` 保存到 store
   - 确保数据在 store 中也得到更新

4. **性能考虑**：
   - `@input` 会频繁触发，但对于少量数据不是问题
   - 如果有性能问题，可以考虑使用防抖（debounce）

## 总结

这次修复的核心是将错误的 `:model-value` + `@change` 组合改为正确的 `v-model` + `@input`（或 `@change`）组合。这是 Vue 3 和 Element Plus 中表单控件的标准用法，确保了输入框的正常工作。

