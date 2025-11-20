# 问题编辑界面 - 快速开始指南

## 🚀 快速启动

### 启动应用
```bash
cd /Users/haolu/Library/CloudStorage/OneDrive-个人/进行中的工作/工程监督/AppDev/CDRLApp
./start-dev.sh
```

### 访问应用
- **前端**：http://localhost:3000
- **后端 API**：http://localhost:8000
- **API 文档**：http://localhost:8000/docs

## 📋 使用流程

### 1. 上传 Word 文档
- 进入导入页面
- 点击"选择文件"上传 Word 文档
- 系统自动识别通知书和问题

### 2. 预览问题
- 查看已识别的问题列表
- 可以选择全选、选择整改通知单或其他问题

### 3. 编辑问题（新功能）
- 点击"✏️ 编辑问题"按钮
- 进入编辑界面
- 在表格中编辑问题字段

### 4. 编辑字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| 标段名称 | 下拉选择 | 支持手动输入新标段 |
| 工点名称 | 文本输入 | 输入工点名称 |
| 问题描述 | 文本域 | 输入问题描述 |
| 问题类别 | 下拉选择 | 工程质量、施工安全等 |
| 问题子类1 | 下拉选择 | 根据类别动态加载 |
| 问题子类2 | 下拉选择 | 根据子类1动态加载 |
| 严重程度 | 下拉选择 | 1-5级 |

### 5. 保存修改
- 修改自动保存到前端状态
- 无需手动保存

### 6. 导入数据库
- 返回问题预览界面
- 选择要导入的问题
- 点击"下一步"进入确认界面
- 点击"保存到数据库"导入

## 🔧 API 端点

### 查询标段列表
```bash
GET /api/sections?project_name=黄百铁路
```

**响应示例**：
```json
{
  "total": 5,
  "data": [
    {
      "id": 1,
      "project_id": 1,
      "section_name": "标段1",
      "contractor_unit": "承包单位",
      "supervisor_unit": "监理单位",
      "designer_unit": "设计单位",
      "testing_unit": "试验单位",
      "created_at": "2025-01-01",
      "updated_at": "2025-01-01"
    }
  ]
}
```

## 📁 关键文件

### 前端
- `frontend/src/components/ImportIssuesEditor.vue` - 编辑组件
- `frontend/src/pages/ImportPage.vue` - 主页面
- `frontend/src/components/ImportPreviewIssues.vue` - 预览组件
- `frontend/src/stores/importStore.js` - 状态管理

### 后端
- `backend/app/main.py` - API 端点
- `backend/app/services/import_service.py` - 导入服务

## 🐛 常见问题

### Q: 编辑后的数据会丢失吗？
A: 不会。修改自动保存到前端状态，直到用户导入数据库。

### Q: 可以添加新的标段吗？
A: 可以。在标段下拉选择中输入新的标段名称即可。

### Q: 问题类别如何级联？
A: 选择第一层类别后，第二层会自动加载相应的子类。

### Q: 如何回滚修改？
A: 刷新页面即可回滚所有修改。

## 📞 技术支持

如有问题，请查看以下文档：
- `IMPORT_EDITOR_IMPLEMENTATION.md` - 详细实现文档
- `EDITOR_IMPLEMENTATION_SUMMARY.md` - 完成总结
- `FINAL_IMPLEMENTATION_REPORT.md` - 最终报告

## ✅ 检查清单

- [ ] 应用已启动
- [ ] 前端可访问（http://localhost:3000）
- [ ] 后端可访问（http://localhost:8000）
- [ ] 可以上传 Word 文档
- [ ] 可以进入编辑界面
- [ ] 可以编辑问题字段
- [ ] 可以导入数据库

---

**版本**：1.0
**最后更新**：2025-11-15

