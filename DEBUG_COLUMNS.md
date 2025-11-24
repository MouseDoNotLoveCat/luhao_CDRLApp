# 调试：施工单位/监理单位列不显示问题

## 问题现象
在"识别问题列表"界面，表格中没有显示"施工单位"和"监理单位"两列。

## 已确认的代码变更
✅ IssuesTable.vue 第140-155行：已添加两列
✅ ImportConfirm.vue 第48-58行：已添加两列
✅ 后端 import_service.py 第410-411、430-431行：已返回 contractor/supervisor 字段
✅ Vite HMR 已触发热更新

## 可能的原因

### 1. 浏览器缓存问题 ⭐ 最可能
**解决方案**：
- 在浏览器中按 `Cmd+Shift+R` (Mac) 或 `Ctrl+Shift+R` (Windows) 强制刷新
- 或者打开开发者工具 (F12)，右键点击刷新按钮，选择"清空缓存并硬性重新加载"

### 2. 表格列被隐藏或滚动到视野外
**检查方法**：
- 在表格中向右滚动，查看是否有更多列
- 检查表格容器的宽度是否足够

### 3. 数据中 contractor/supervisor 字段为空
**检查方法**：
1. 打开浏览器开发者工具 (F12)
2. 切换到 Console 标签
3. 查找识别响应的日志：`📥 收到识别响应:`
4. 展开 `issues` 数组，检查每个问题对象是否包含 `contractor` 和 `supervisor` 字段

**预期数据结构**：
```javascript
{
  success: true,
  issues: [
    {
      id: "temp_0",
      section_name: "YCZQ-4标",
      section_code: "YCZQ-4",
      contractor: "中铁五局",      // ← 应该有这个字段
      supervisor: "中铁路安",      // ← 应该有这个字段
      site_name: "路基DK262+635.41～DK263+079.5段",
      description: "...",
      // ... 其他字段
    }
  ]
}
```

### 4. 前端组件未正确重新渲染
**解决方案**：
- 停止开发服务器 (Ctrl+C)
- 重新运行 `./start-dev.sh`
- 重新打开浏览器访问 http://localhost:3000

## 调试步骤（按顺序执行）

### 步骤1：检查浏览器控制台
1. 打开浏览器开发者工具 (F12)
2. 切换到 Console 标签
3. 上传测试文档
4. 查找日志：`📥 收到识别响应:`
5. 展开响应数据，检查 `issues[0]` 是否包含 `contractor` 和 `supervisor`

### 步骤2：检查网络请求
1. 切换到 Network 标签
2. 上传测试文档
3. 找到 `/import/recognize` 请求
4. 点击查看 Response
5. 确认返回的 JSON 中包含 `contractor` 和 `supervisor` 字段

### 步骤3：检查 DOM 元素
1. 切换到 Elements 标签
2. 找到表格的 `<table>` 元素
3. 查看 `<thead>` 中是否有"施工单位"和"监理单位"列头
4. 查看 `<tbody>` 中是否有对应的单元格

### 步骤4：强制刷新浏览器
- Mac: `Cmd+Shift+R`
- Windows: `Ctrl+Shift+R`
- 或者：右键点击刷新按钮 → "清空缓存并硬性重新加载"

### 步骤5：重启开发服务器
```bash
# 在终端中按 Ctrl+C 停止服务
# 然后重新运行
./start-dev.sh
```

### 步骤6：清除浏览器缓存
1. 打开浏览器设置
2. 清除浏览器缓存和 Cookie
3. 重新访问 http://localhost:3000

## 验证列是否正确添加

### 检查 IssuesTable.vue
```bash
# 在终端运行
grep -n "施工单位\|监理单位" frontend/src/components/IssuesTable.vue
```

**预期输出**：
```
140:      <el-table-column prop="contractor" label="施工单位" width="160" show-overflow-tooltip>
149:      <el-table-column prop="supervisor" label="监理单位" width="160" show-overflow-tooltip>
576:        <el-form-item label="施工单位">
579:        <el-form-item label="监理单位">
```

### 检查 ImportConfirm.vue
```bash
# 在终端运行
grep -n "施工单位\|监理单位" frontend/src/components/ImportConfirm.vue
```

**预期输出**：
```
49:          <el-table-column prop="contractor" label="施工单位" width="160" show-overflow-tooltip>
54:          <el-table-column prop="supervisor" label="监理单位" width="160" show-overflow-tooltip>
```

## 如果问题仍然存在

### 方案A：检查表格宽度
表格可能因为列太多而需要横向滚动。尝试：
1. 在表格中向右滚动
2. 或者缩小浏览器窗口宽度，看是否出现横向滚动条

### 方案B：临时调整列顺序
如果怀疑列被隐藏，可以临时将"施工单位"和"监理单位"列移到表格最前面（序号之后）：

```vue
<!-- 临时调整：将施工/监理单位移到最前面 -->
<el-table-column type="index" label="序号" width="60" />
<el-table-column prop="contractor" label="施工单位" width="160" show-overflow-tooltip />
<el-table-column prop="supervisor" label="监理单位" width="160" show-overflow-tooltip />
<el-table-column prop="inspection_date" label="检查时间" width="120" />
<!-- ... 其他列 -->
```

### 方案C：添加调试日志
在 IssuesTable.vue 的 `<script setup>` 部分添加：

```javascript
import { watch } from 'vue'

watch(() => importStore.recognizedIssues, (newIssues) => {
  console.log('🔍 识别到的问题数据:', newIssues)
  if (newIssues.length > 0) {
    console.log('🔍 第一个问题的数据:', newIssues[0])
    console.log('🔍 contractor:', newIssues[0].contractor)
    console.log('🔍 supervisor:', newIssues[0].supervisor)
  }
}, { immediate: true, deep: true })
```

---

**请先尝试步骤1-4，特别是强制刷新浏览器（步骤4）！**

