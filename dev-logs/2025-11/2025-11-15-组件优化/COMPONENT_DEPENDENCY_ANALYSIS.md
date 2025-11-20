# 组件依赖关系分析

## 📊 组件使用关系图

### Pages 使用的 Components

```
ImportPage.vue
├── IssuesTable.vue
├── NoticesList (已删除 - 未使用)
├── IssuesPreview.vue
└── IssueDetailPreview.vue

IssueDetailPage.vue
└── (独立页面，无组件依赖)

IssuesPage.vue
├── IssuesTable.vue
└── (其他功能)

NoticeManagementPage.vue
├── NoticesListComponent.vue
├── IssuesPreview.vue
└── IssueDetailPreview.vue

ProjectManagementPage.vue
├── ProjectsList.vue
├── ProjectForm.vue
├── SectionsList.vue
└── SectionForm.vue
```

## 🔄 状态管理依赖

### importStore 使用位置
- ImportPage.vue
- IssuesPreview.vue
- IssueDetailPreview.vue

### noticeManagementStore 使用位置
- NoticeManagementPage.vue
- IssuesPreview.vue
- IssueDetailPreview.vue

### projectManagementStore 使用位置
- ProjectManagementPage.vue
- ProjectsList.vue
- ProjectForm.vue
- SectionsList.vue
- SectionForm.vue

## 🎯 核心组件分析

### 高复用度组件
1. **IssuesTable.vue** (1008 行)
   - 用途: 问题数据表格展示
   - 使用位置: ImportPage, IssuesPage
   - 功能: 搜索、过滤、分页、行内编辑

2. **IssuesPreview.vue** (284 行)
   - 用途: 问题列表预览
   - 使用位置: ImportPage, NoticeManagementPage
   - 功能: 统计、搜索、分页

3. **IssueDetailPreview.vue** (295 行)
   - 用途: 问题详情预览
   - 使用位置: ImportPage, NoticeManagementPage
   - 功能: 详情展示、导航

### 中等复用度组件
- NoticesListComponent.vue - 通知书列表
- ProjectsList.vue - 项目列表
- SectionsList.vue - 分项列表

### 低复用度组件
- ProjectForm.vue - 项目表单
- SectionForm.vue - 分项表单

## 🗑️ 已删除的文件

1. **MatchingResultAlert.vue** (0 行)
   - 原因: 空文件，未被任何地方使用
   - 删除时间: 2025-11-13

2. **NoticesList.vue** (0 行)
   - 原因: 空文件，未被任何地方使用
   - 删除时间: 2025-11-13
   - 注: NoticesListComponent.vue 是其替代品

## 💡 优化建议

### 可合并的组件
1. **NoticesList.vue** + **NoticesListComponent.vue**
   - 建议: 保留 NoticesListComponent.vue，删除 NoticesList.vue
   - 状态: ✓ 已完成

2. **IssuesPreview.vue** + **IssuesTable.vue**
   - 建议: 保持分离（不同用途）
   - 状态: ✓ 无需修改

### 可提取的公共逻辑
- 搜索和过滤逻辑
- 分页逻辑
- 数据加载逻辑

## 📈 项目健康度

| 指标 | 状态 | 说明 |
|------|------|------|
| 编译错误 | ✓ 无 | 所有 Vue 文件有效 |
| 未使用文件 | ✓ 已清理 | 删除 2 个空文件 |
| 循环依赖 | ✓ 无 | 依赖关系清晰 |
| 代码重复 | ⚠️ 中等 | 可进一步优化 |

