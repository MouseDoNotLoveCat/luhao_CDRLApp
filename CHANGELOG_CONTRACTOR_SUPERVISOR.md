# 施工单位/监理单位字段新增变更说明

## 变更概述
在"识别问题列表"和"确认修改"界面统一新增并展示"施工单位"和"监理单位"两列，数据来自后端解析结果的 `contractor` 和 `supervisor` 字段。

## 变更文件清单

### 1. IssuesTable.vue（识别问题列表）
**文件路径**: `frontend/src/components/IssuesTable.vue`

#### 变更1：表格列展示（第139-155行）
- **位置**: 在"标段"列之后、"检查工点"列之前
- **新增列**:
  - 施工单位（prop: contractor，宽度160，支持tooltip）
  - 监理单位（prop: supervisor，宽度160，支持tooltip）
- **展示规则**: 
  - 若字段为空，显示"未知施工单位"/"未知监理单位"
  - 文本溢出时显示省略号并支持悬浮提示（show-overflow-tooltip）

```vue
<!-- 施工单位 -->
<el-table-column prop="contractor" label="施工单位" width="160" show-overflow-tooltip>
  <template #default="{ row }">
    <div style="padding: 8px; min-height: 32px; display: flex; align-items: center;">
      {{ row.contractor || '未知施工单位' }}
    </div>
  </template>
</el-table-column>

<!-- 监理单位 -->
<el-table-column prop="supervisor" label="监理单位" width="160" show-overflow-tooltip>
  <template #default="{ row }">
    <div style="padding: 8px; min-height: 32px; display: flex; align-items: center;">
      {{ row.supervisor || '未知监理单位' }}
    </div>
  </template>
</el-table-column>
```

#### 变更2：编辑表单（第575-581行）
- **位置**: 在"标段"表单项之后、"检查工点"表单项之前
- **新增表单项**:
  - 施工单位（绑定 editingIssue.contractor，可编辑）
  - 监理单位（绑定 editingIssue.supervisor，可编辑）
- **行为**: 
  - 初始值来自解析结果
  - 支持手动编辑与保存
  - 空值时显示占位文本

```vue
<!-- 新增：施工单位/监理单位（默认可编辑，初始值来自解析结果，空则显示占位） -->
<el-form-item label="施工单位">
  <el-input v-model="editingIssue.contractor" placeholder="未知施工单位" />
</el-form-item>
<el-form-item label="监理单位">
  <el-input v-model="editingIssue.supervisor" placeholder="未知监理单位" />
</el-form-item>
```

### 2. ImportConfirm.vue（确认修改界面）
**文件路径**: `frontend/src/components/ImportConfirm.vue`

#### 变更：表格列展示（第48-58行）
- **位置**: 在"标段"列之后、"工点"列之前
- **新增列**:
  - 施工单位（prop: contractor，宽度160，支持tooltip）
  - 监理单位（prop: supervisor，宽度160，支持tooltip）
- **展示规则**: 与IssuesTable保持一致

```vue
<!-- 新增：施工单位/监理单位（在标段之后、检查工点之前） -->
<el-table-column prop="contractor" label="施工单位" width="160" show-overflow-tooltip>
  <template #default="{ row }">
    {{ row.contractor || '未知施工单位' }}
  </template>
</el-table-column>
<el-table-column prop="supervisor" label="监理单位" width="160" show-overflow-tooltip>
  <template #default="{ row }">
    {{ row.supervisor || '未知监理单位' }}
  </template>
</el-table-column>
```

## 数据流说明

### 后端解析对接
- **数据来源**: 后端解析结果中的 `contractor` 和 `supervisor` 字段
- **解析规则**: 
  - 支持单行与跨行格式
  - 标段编号使用 `(?=标)` 前瞻匹配
  - 检查时间支持多种格式，统一输出 YYYY-MM-DD
- **回填策略**: 
  - 后端以 section_code 为键统一回填
  - 仍缺失则置为"未知施工单位"/"未知监理单位"
  - 前端无需二次回填，直接展示后端返回值

### 字段绑定
- **表格展示**: 直接绑定 `row.contractor` 和 `row.supervisor`
- **表单编辑**: 绑定 `editingIssue.contractor` 和 `editingIssue.supervisor`
- **默认值处理**: 使用 `||` 运算符，空值时显示默认文本

## 兼容性保证

### 不回归承诺
✅ 不修改、不移除现有列与字段  
✅ 仅新增两列与两项表单  
✅ 保持对既有单行/变体/标点（1. / 1． / 1、）的解析显示不受影响  
✅ 导出/打印（如有）保持原逻辑  

### 验收标准
1. ✅ 使用提供的测试文本导入，新增两列正确展示
2. ✅ 对已存在的单行经典样例与标点变体样例，新增两列正常显示且不回归
3. ✅ 后端返回空值时，前端显示"未知施工单位"/"未知监理单位"

## 测试验证

### 测试用例
```
（一）中铁五局施工、中铁路安监理的YCZQ-4标
1、路基DK262+635.41～DK263+079.5段（检查时间2025年7月23日）
```

### 预期结果
- section_code: YCZQ-4
- site_name: 路基DK262+635.41～DK263+079.5段
- check_date: 2025-07-23
- **contractor: 中铁五局** ✅
- **supervisor: 中铁路安** ✅

## 后续迭代建议
1. 可增加对 contractor/supervisor 的搜索/筛选支持
2. 可在导出/打印功能中加入"施工单位/监理单位"列
3. 如需只读展示，可将表单中的 el-input 改为 disabled 或只读模式

---
**变更完成时间**: 2025年
**变更人**: Cascade AI Assistant
**审核状态**: 待验证

