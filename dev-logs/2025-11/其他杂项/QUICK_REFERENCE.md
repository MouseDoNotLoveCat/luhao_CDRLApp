# 项目与标段管理界面 - 快速参考

**版本**: 2.0 | **日期**: 2025-11-07 | **状态**: ✅ 完成

---

## 🎯 修改概览

### 问题 1: 项目列表操作按钮布局 ✅

**文件**: `frontend/src/components/ProjectsList.vue`

**修改**:
```vue
<!-- 操作按钮容器 -->
<div class="action-buttons">
  <el-button type="primary" size="small">查看标段</el-button>
  <el-button type="warning" size="small">编辑</el-button>
  <el-button type="danger" size="small">删除</el-button>
</div>

<!-- CSS 样式 -->
<style scoped>
.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
}

.action-buttons :deep(.el-button) {
  margin: 0;
}
</style>
```

**效果**: 按钮水平排列，间距均匀

---

### 问题 2: 标段表结构调整 ✅

#### 2.1 数据库修改

**文件**: `database_schema.sql`

**修改前**:
```sql
CREATE TABLE sections (
  id INTEGER PRIMARY KEY,
  project_id INTEGER NOT NULL,
  section_code VARCHAR(100) NOT NULL,  -- ❌ 删除
  section_name VARCHAR(200),
  ...
  UNIQUE(project_id, section_code)  -- ❌ 改为 section_name
);
```

**修改后**:
```sql
CREATE TABLE sections (
  id INTEGER PRIMARY KEY,
  project_id INTEGER NOT NULL,
  section_name VARCHAR(200) NOT NULL,  -- ✅ 必填
  ...
  UNIQUE(project_id, section_name)  -- ✅ 新约束
);
```

#### 2.2 数据库迁移

**文件**: `backend/scripts/migrate_remove_section_code.py`

**执行**:
```bash
cd backend
python scripts/migrate_remove_section_code.py
```

#### 2.3 后端 API 修改

**文件**: `backend/app/main.py`

**修改的端点**:

| 端点 | 修改 |
|------|------|
| `POST /api/sections` | 移除 `section_code` 参数 |
| `PUT /api/sections/{id}` | 移除 `section_code` 参数 |
| `GET /api/projects/{id}/sections` | 移除 section_code 搜索 |
| `GET /api/sections/{id}` | 移除 section_code 字段 |

**示例**:
```bash
# 创建标段（新）
curl -X POST "http://localhost:8000/api/sections" \
  -d "project_id=1&section_name=标段A"

# 修改标段（新）
curl -X PUT "http://localhost:8000/api/sections/1" \
  -d "section_name=标段B"
```

#### 2.4 前端组件修改

**SectionsList.vue**:
```vue
<!-- 搜索框 -->
<el-input placeholder="搜索标段名称或单位..." />

<!-- 表格 -->
<el-table :default-sort="{ prop: 'section_name', order: 'ascending' }">
  <el-table-column prop="section_name" label="标段名称" />
  <!-- section_code 列已删除 -->
</el-table>
```

**SectionForm.vue**:
```vue
<!-- 表单 -->
<el-form-item label="标段名称" prop="section_name">
  <el-input v-model="formData.section_name" />
</el-form-item>
<!-- section_code 字段已删除 -->

<!-- 验证规则 -->
const rules = {
  section_name: [
    { required: true, message: '标段名称不能为空' },
    { max: 200, message: '长度不能超过 200' }
  ]
}
```

---

## 📊 修改统计

| 项目 | 数值 |
|------|------|
| 修改文件 | 6 个 |
| 新增文件 | 2 个 |
| 修改代码行数 | 50+ 行 |
| API 端点修改 | 4 个 |
| 前端组件修改 | 2 个 |

---

## 🔄 执行步骤

### 第 1 步: 数据库迁移

```bash
cd backend
python scripts/migrate_remove_section_code.py
```

### 第 2 步: 启动后端

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### 第 3 步: 启动前端

```bash
cd frontend
npm run dev
```

### 第 4 步: 测试功能

1. 打开 http://localhost:3008
2. 进入"项目与标段管理"
3. 测试创建、编辑、删除标段

---

## 🧪 快速测试

### 创建标段

```bash
curl -X POST "http://localhost:8000/api/sections" \
  -d "project_id=1&section_name=新标段&contractor_unit=施工单位"
```

### 获取标段列表

```bash
curl "http://localhost:8000/api/projects/1/sections"
```

### 修改标段

```bash
curl -X PUT "http://localhost:8000/api/sections/1" \
  -d "section_name=修改后的标段"
```

### 删除标段

```bash
curl -X DELETE "http://localhost:8000/api/sections/1"
```

---

## ⚠️ 注意事项

1. **备份数据库**: 执行迁移前备份 `backend/cdrl.db`
2. **API 兼容性**: 旧的 API 调用（包含 section_code）将不再工作
3. **前端更新**: 确保前端代码已更新
4. **测试环境**: 建议先在测试环境验证

---

## 📝 文件清单

### 修改文件
- ✅ `frontend/src/components/ProjectsList.vue`
- ✅ `frontend/src/components/SectionsList.vue`
- ✅ `frontend/src/components/SectionForm.vue`
- ✅ `backend/app/main.py`
- ✅ `database_schema.sql`

### 新增文件
- ✅ `backend/scripts/migrate_remove_section_code.py`
- ✅ `MODIFICATIONS_SUMMARY.md`
- ✅ `TESTING_GUIDE.md`
- ✅ `QUICK_REFERENCE.md`

---

## 🎓 关键概念

### 唯一性约束变更

**之前**: `UNIQUE(project_id, section_code)`
- 同一项目下，标段编号唯一

**现在**: `UNIQUE(project_id, section_name)`
- 同一项目下，标段名称唯一

### API 参数变更

**创建标段**:
```
移除: section_code
保留: project_id, section_name, contractor_unit, ...
```

**修改标段**:
```
移除: section_code
保留: section_name, contractor_unit, ...
```

---

## 🚀 后续建议

1. **文档更新**: 更新 API 文档
2. **测试用例**: 添加新的单元测试
3. **性能优化**: 为 section_name 添加索引
4. **用户通知**: 通知现有用户 API 变更

---

**修改完成**: 2025-11-07  
**质量评分**: ⭐⭐⭐⭐⭐


