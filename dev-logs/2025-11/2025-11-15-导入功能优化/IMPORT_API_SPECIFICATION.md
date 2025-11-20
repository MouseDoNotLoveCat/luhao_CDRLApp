# CDRLApp 导入功能 - API 规范

## 1. 识别 API（修改现有）

### 端点
```
POST /api/import/document
```

### 说明
识别 Word 文档中的通知书和问题，返回识别结果（不导入数据库）。

### 请求

**Content-Type**: `multipart/form-data`

**参数**:
```
file: <binary> - Word 文档文件
```

### 响应

**状态码**: 200 OK

**响应体**:
```json
{
  "success": true,
  "notice": {
    "id": "temp_550e8400-e29b-41d4-a716-446655440000",
    "notice_number": "南宁站[2025]（通知）黄百10号",
    "check_date": "2025-08-20",
    "check_unit": "南宁监督站",
    "check_personnel": "李规录、陈胜",
    "project_name": "黄百铁路",
    "builder_unit": "云桂铁路广西有限责任公司",
    "issues_count": 65
  },
  "issues": [
    {
      "id": "temp_issue_1",
      "notice_id": "temp_550e8400-e29b-41d4-a716-446655440000",
      "site_name": "工点 1",
      "description": "混凝土强度不足",
      "issue_category": "工程质量",
      "severity": 3,
      "rectification_deadline": "2025-09-20",
      "responsible_unit": "施工单位",
      "responsible_person": "张三",
      "is_rectification_notice": true,
      "document_section": "rectification",
      "status": "pending",
      "created_at": "2025-11-14T10:00:00Z"
    }
  ]
}
```

### 错误响应

**状态码**: 400 Bad Request

```json
{
  "success": false,
  "error": "文件格式不支持，请上传 Word 文档"
}
```

**状态码**: 500 Internal Server Error

```json
{
  "success": false,
  "error": "识别失败：文档解析错误"
}
```

---

## 2. 批量识别 API（修改现有）

### 端点
```
POST /api/import/batch
```

### 说明
批量识别多个 Word 文档，返回识别结果列表。

### 请求

**Content-Type**: `multipart/form-data`

**参数**:
```
files: <binary[]> - Word 文档文件数组
```

### 响应

**状态码**: 200 OK

```json
{
  "success": true,
  "total_files": 3,
  "successful_files": 3,
  "failed_files": 0,
  "results": [
    {
      "file_name": "通知书1.docx",
      "success": true,
      "notice": { ... },
      "issues": [ ... ]
    },
    {
      "file_name": "通知书2.docx",
      "success": true,
      "notice": { ... },
      "issues": [ ... ]
    }
  ],
  "errors": []
}
```

---

## 3. 导入选中记录 API（新增）

### 端点
```
POST /api/notices/import-selected
```

### 说明
导入用户选中的通知书和问题到数据库。

### 请求

**Content-Type**: `application/json`

**请求体**:
```json
{
  "notice": {
    "notice_number": "南宁站[2025]（通知）黄百10号",
    "check_date": "2025-08-20",
    "check_unit": "南宁监督站",
    "check_personnel": "李规录、陈胜",
    "project_name": "黄百铁路",
    "builder_unit": "云桂铁路广西有限责任公司"
  },
  "issues": [
    {
      "site_name": "工点 1",
      "description": "混凝土强度不足",
      "issue_category": "工程质量",
      "severity": 3,
      "rectification_deadline": "2025-09-20",
      "responsible_unit": "施工单位",
      "responsible_person": "张三",
      "is_rectification_notice": true,
      "document_section": "rectification"
    },
    {
      "site_name": "工点 2",
      "description": "钢筋绑扎不规范",
      "issue_category": "工程质量",
      "severity": 2,
      "rectification_deadline": "2025-09-25",
      "responsible_unit": "施工单位",
      "responsible_person": "李四",
      "is_rectification_notice": true,
      "document_section": "rectification"
    }
  ]
}
```

### 响应

**状态码**: 200 OK

```json
{
  "success": true,
  "notice_id": 123,
  "imported_issues_count": 2,
  "errors": []
}
```

### 错误响应

**状态码**: 400 Bad Request

```json
{
  "success": false,
  "error": "通知书编号已存在",
  "notice_number": "南宁站[2025]（通知）黄百10号"
}
```

**状态码**: 422 Unprocessable Entity

```json
{
  "success": false,
  "error": "数据验证失败",
  "errors": [
    {
      "field": "notice.check_date",
      "message": "日期格式不正确"
    },
    {
      "field": "issues[0].description",
      "message": "问题描述不能为空"
    }
  ]
}
```

**状态码**: 500 Internal Server Error

```json
{
  "success": false,
  "error": "导入失败：数据库错误",
  "details": "UNIQUE constraint failed: supervision_notices.notice_number"
}
```

---

## 4. 批量导入选中记录 API（新增）

### 端点
```
POST /api/notices/import-batch-selected
```

### 说明
批量导入多个通知书和问题。

### 请求

**Content-Type**: `application/json`

**请求体**:
```json
{
  "batch": [
    {
      "notice": { ... },
      "issues": [ ... ]
    },
    {
      "notice": { ... },
      "issues": [ ... ]
    }
  ]
}
```

### 响应

**状态码**: 200 OK

```json
{
  "success": true,
  "total_notices": 2,
  "imported_notices": 2,
  "failed_notices": 0,
  "total_issues": 65,
  "imported_issues": 65,
  "failed_issues": 0,
  "results": [
    {
      "notice_number": "南宁站[2025]（通知）黄百10号",
      "success": true,
      "notice_id": 123,
      "imported_issues_count": 32
    },
    {
      "notice_number": "南宁站[2025]（通知）黄百11号",
      "success": true,
      "notice_id": 124,
      "imported_issues_count": 33
    }
  ],
  "errors": []
}
```

---

## 5. 数据验证规则

### 通知书验证
```javascript
{
  "notice_number": {
    "required": true,
    "type": "string",
    "min_length": 1,
    "max_length": 100,
    "pattern": "^[\\u4e00-\\u9fa5a-zA-Z0-9\\[\\]（）\\-]+$"
  },
  "check_date": {
    "required": true,
    "type": "date",
    "format": "YYYY-MM-DD"
  },
  "check_unit": {
    "required": true,
    "type": "string",
    "min_length": 1,
    "max_length": 100
  },
  "project_name": {
    "required": true,
    "type": "string",
    "min_length": 1,
    "max_length": 100
  }
}
```

### 问题验证
```javascript
{
  "description": {
    "required": true,
    "type": "string",
    "min_length": 1,
    "max_length": 500
  },
  "site_name": {
    "required": true,
    "type": "string",
    "min_length": 1,
    "max_length": 100
  },
  "issue_category": {
    "required": true,
    "type": "enum",
    "values": ["工程质量", "安全隐患", "其他"]
  },
  "severity": {
    "required": false,
    "type": "integer",
    "min": 1,
    "max": 5
  },
  "rectification_deadline": {
    "required": false,
    "type": "date",
    "format": "YYYY-MM-DD"
  }
}
```

---

## 6. 错误代码

| 代码 | 说明 |
|------|------|
| 400 | 请求参数错误 |
| 422 | 数据验证失败 |
| 500 | 服务器错误 |
| 409 | 数据冲突（如通知书编号重复） |

---

## 7. 后端实现示例

### Python (FastAPI)

```python
@app.post("/api/import/document")
async def import_document(file: UploadFile = File(...)):
    """识别 Word 文档"""
    try:
        # 保存临时文件
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        
        # 识别文档
        service = ImportService(str(DB_PATH))
        result = service.import_word_document(temp_path)
        
        # 删除临时文件
        os.remove(temp_path)
        
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/notices/import-selected")
async def import_selected(data: dict):
    """导入选中的记录"""
    try:
        service = ImportService(str(DB_PATH))
        result = service.import_selected_records(data)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}
```

---

## 8. 前端调用示例

### JavaScript (Axios)

```javascript
// 识别文档
async function recognizeDocument(file) {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await axios.post('/api/import/document', formData)
  return response.data
}

// 导入选中的记录
async function importSelected(notice, issues) {
  const response = await axios.post('/api/notices/import-selected', {
    notice,
    issues
  })
  return response.data
}
```

---

## 9. 性能指标

| 指标 | 目标 | 说明 |
|------|------|------|
| 识别速度 | < 5s | 单个 Word 文档 |
| 导入速度 | < 2s | 100 条问题 |
| 批量导入 | < 10s | 10 个文档 |
| 响应时间 | < 100ms | API 响应 |

---

## 10. 安全考虑

- [ ] 验证文件类型（只允许 .docx）
- [ ] 限制文件大小（最大 10MB）
- [ ] 验证用户权限
- [ ] 记录操作日志
- [ ] 使用事务处理确保数据一致性
- [ ] 防止 SQL 注入
- [ ] 防止 XSS 攻击

---

**版本**: v1.0
**更新**: 2025-11-14
**状态**: 待审批

