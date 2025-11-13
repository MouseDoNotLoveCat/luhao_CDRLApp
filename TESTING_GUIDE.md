# 项目与标段管理界面 - 测试指南

**日期**: 2025-11-07  
**版本**: 2.0  
**测试状态**: 🔄 进行中

---

## 📋 测试清单

### 1️⃣ 数据库迁移测试

#### 1.1 执行迁移脚本

```bash
# 进入后端目录
cd backend

# 执行迁移脚本
python scripts/migrate_remove_section_code.py
```

**预期输出**:
```
🔄 开始迁移数据库...
📋 当前表结构:
   - id (INTEGER)
   - project_id (INTEGER)
   - section_code (VARCHAR(100))
   - section_name (VARCHAR(200))
   - contractor_unit (VARCHAR(100))
   - supervisor_unit (VARCHAR(100))
   - designer_unit (VARCHAR(100))
   - testing_unit (VARCHAR(100))
   - created_at (TIMESTAMP)
   - updated_at (TIMESTAMP)

📝 步骤 1: 创建新表...
✅ 新表创建成功

📝 步骤 2: 迁移数据...
✅ 数据迁移成功 (X 条记录)

📝 步骤 3: 删除旧表...
✅ 旧表删除成功

📝 步骤 4: 重命名新表...
✅ 新表重命名成功

📝 步骤 5: 重建索引...
✅ 索引重建成功

✅ 迁移完成！
```

#### 1.2 验证表结构

```bash
# 查看表结构
sqlite3 cdrl.db "PRAGMA table_info(sections)"
```

**预期结果**:
```
0|id|INTEGER|0||1
1|project_id|INTEGER|1||0
2|section_name|VARCHAR(200)|1||0
3|contractor_unit|VARCHAR(100)|0||0
4|supervisor_unit|VARCHAR(100)|0||0
5|designer_unit|VARCHAR(100)|0||0
6|testing_unit|VARCHAR(100)|0||0
7|created_at|TIMESTAMP|0||0
8|updated_at|TIMESTAMP|0||0
```

**验证点**:
- ✅ section_code 字段已删除
- ✅ section_name 字段存在且为 NOT NULL
- ✅ 没有 section_code 字段

#### 1.3 验证唯一性约束

```bash
# 查看表的索引和约束
sqlite3 cdrl.db "SELECT sql FROM sqlite_master WHERE type='table' AND name='sections'"
```

**预期结果**:
```
UNIQUE(project_id, section_name)
```

---

### 2️⃣ 后端 API 测试

#### 2.1 启动后端服务

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

#### 2.2 创建标段 API 测试

```bash
# 创建标段（新参数）
curl -X POST "http://localhost:8000/api/sections" \
  -d "project_id=1&section_name=新标段&contractor_unit=施工单位&supervisor_unit=监理单位"
```

**预期结果**:
```json
{
  "id": 1,
  "project_id": 1,
  "section_name": "新标段",
  "contractor_unit": "施工单位",
  "supervisor_unit": "监理单位",
  "designer_unit": "",
  "testing_unit": "",
  "message": "标段创建成功"
}
```

**验证点**:
- ✅ 返回数据中没有 section_code 字段
- ✅ section_name 字段存在
- ✅ 创建成功消息

#### 2.3 获取标段列表 API 测试

```bash
# 获取标段列表
curl "http://localhost:8000/api/projects/1/sections"
```

**预期结果**:
```json
{
  "total": 1,
  "data": [
    {
      "id": 1,
      "project_id": 1,
      "section_name": "新标段",
      "contractor_unit": "施工单位",
      "supervisor_unit": "监理单位",
      "designer_unit": "",
      "testing_unit": "",
      "created_at": "2025-11-07T10:00:00",
      "updated_at": "2025-11-07T10:00:00"
    }
  ]
}
```

**验证点**:
- ✅ 返回数据中没有 section_code 字段
- ✅ 按 section_name 排序
- ✅ 分页正常

#### 2.4 修改标段 API 测试

```bash
# 修改标段
curl -X PUT "http://localhost:8000/api/sections/1" \
  -d "section_name=修改后的标段&contractor_unit=新施工单位"
```

**预期结果**:
```json
{
  "id": 1,
  "project_id": 1,
  "section_name": "修改后的标段",
  "contractor_unit": "新施工单位",
  "message": "标段修改成功"
}
```

**验证点**:
- ✅ section_name 已更新
- ✅ 没有 section_code 参数
- ✅ 修改成功消息

#### 2.5 唯一性约束测试

```bash
# 尝试创建重复的标段名称
curl -X POST "http://localhost:8000/api/sections" \
  -d "project_id=1&section_name=修改后的标段"
```

**预期结果**:
```json
{
  "detail": "该项目下标段名称已存在"
}
```

**验证点**:
- ✅ 返回 400 错误
- ✅ 错误消息提示标段名称已存在

---

### 3️⃣ 前端功能测试

#### 3.1 启动前端服务

```bash
cd frontend
npm run dev
```

#### 3.2 项目列表操作按钮测试

**测试步骤**:
1. 打开浏览器访问 http://localhost:3008
2. 点击"项目与标段管理"菜单
3. 查看项目列表

**验证点**:
- ✅ 操作按钮（查看标段、编辑、删除）在同一行水平排列
- ✅ 按钮之间有适当的间距
- ✅ 按钮不会换行

#### 3.3 创建标段测试

**测试步骤**:
1. 在项目列表中选择一个项目
2. 点击"查看标段"按钮
3. 点击"新建标段"按钮
4. 填写标段名称（例如：标段A）
5. 填写其他信息（可选）
6. 点击"创建"按钮

**验证点**:
- ✅ 表单中没有"标段编号"字段
- ✅ "标段名称"字段为必填
- ✅ 创建成功后返回标段列表
- ✅ 新标段显示在列表中

#### 3.4 编辑标段测试

**测试步骤**:
1. 在标段列表中选择一个标段
2. 点击"编辑"按钮
3. 修改标段名称
4. 点击"更新"按钮

**验证点**:
- ✅ 编辑表单中没有"标段编号"字段
- ✅ 标段名称已预填
- ✅ 修改成功后返回标段列表
- ✅ 标段名称已更新

#### 3.5 删除标段测试

**测试步骤**:
1. 在标段列表中选择一个标段
2. 点击"删除"按钮
3. 在确认对话框中点击"确定"

**验证点**:
- ✅ 确认消息使用标段名称（不是标段编号）
- ✅ 删除成功后标段从列表中移除
- ✅ 显示"标段删除成功"消息

#### 3.6 搜索标段测试

**测试步骤**:
1. 在标段列表中输入搜索关键词
2. 查看搜索结果

**验证点**:
- ✅ 搜索框提示文本为"搜索标段名称或单位..."
- ✅ 搜索功能正常工作
- ✅ 按标段名称排序

---

## 🐛 常见问题排查

### 问题 1: 迁移脚本执行失败

**症状**: 执行迁移脚本时出现错误

**解决方案**:
1. 确保数据库文件存在：`backend/cdrl.db`
2. 确保数据库不被其他进程占用
3. 检查数据库权限

### 问题 2: API 返回 400 错误

**症状**: 创建或修改标段时返回 400 错误

**解决方案**:
1. 检查 section_name 是否为空
2. 检查 project_id 是否有效
3. 检查标段名称是否已存在

### 问题 3: 前端表单显示错误

**症状**: 前端表单显示异常

**解决方案**:
1. 清除浏览器缓存
2. 重新启动前端服务
3. 检查浏览器控制台是否有错误

---

## ✅ 测试完成检查表

- [ ] 数据库迁移成功
- [ ] 表结构验证正确
- [ ] 唯一性约束验证正确
- [ ] 创建标段 API 测试通过
- [ ] 获取标段列表 API 测试通过
- [ ] 修改标段 API 测试通过
- [ ] 唯一性约束 API 测试通过
- [ ] 项目列表操作按钮显示正确
- [ ] 创建标段功能正常
- [ ] 编辑标段功能正常
- [ ] 删除标段功能正常
- [ ] 搜索标段功能正常

---

**测试日期**: 2025-11-07  
**测试人员**: [待填写]  
**测试结果**: [待填写]


