# 项目与标段管理 - API 参考文档

**版本**: 1.0  
**日期**: 2025-11-07  
**基础 URL**: `http://localhost:8000/api`

---

## 📋 项目 API

### 获取项目列表

**请求**:
```http
GET /projects?search=&limit=100&offset=0
```

**参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| search | string | 否 | 搜索关键词（项目名称或建设单位） |
| limit | integer | 否 | 每页数量，默认 100 |
| offset | integer | 否 | 偏移量，默认 0 |

**响应**:
```json
{
  "total": 4,
  "data": [
    {
      "id": 1,
      "project_name": "黄百铁路广西段",
      "builder_unit": "云桂铁路广西有限责任公司",
      "sections_count": 5
    }
  ]
}
```

---

### 获取单个项目

**请求**:
```http
GET /projects/{project_id}
```

**参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| project_id | integer | 是 | 项目 ID |

**响应**:
```json
{
  "id": 1,
  "project_name": "黄百铁路广西段",
  "builder_unit": "云桂铁路广西有限责任公司",
  "created_at": "2025-11-07 07:29:23",
  "updated_at": "2025-11-07 07:29:23"
}
```

---

### 创建项目

**请求**:
```http
POST /projects?project_name=新项目&builder_unit=建设单位
```

**参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| project_name | string | 是 | 项目名称（2-200 字符） |
| builder_unit | string | 否 | 建设单位 |

**响应**:
```json
{
  "id": 6,
  "project_name": "新项目",
  "builder_unit": "建设单位",
  "sections_count": 0,
  "message": "项目创建成功"
}
```

---

### 修改项目

**请求**:
```http
PUT /projects/{project_id}?project_name=修改后的项目&builder_unit=修改后的建设单位
```

**参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| project_id | integer | 是 | 项目 ID |
| project_name | string | 是 | 项目名称 |
| builder_unit | string | 否 | 建设单位 |

**响应**:
```json
{
  "id": 6,
  "project_name": "修改后的项目",
  "builder_unit": "修改后的建设单位",
  "message": "项目修改成功"
}
```

---

### 删除项目

**请求**:
```http
DELETE /projects/{project_id}?cascade=false
```

**参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| project_id | integer | 是 | 项目 ID |
| cascade | boolean | 否 | 是否级联删除标段，默认 false |

**响应**:
```json
{
  "success": true,
  "message": "项目删除成功",
  "deleted_sections": 0
}
```

---

## 📋 标段 API

### 获取标段列表

**请求**:
```http
GET /projects/{project_id}/sections?search=&limit=100&offset=0
```

**参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| project_id | integer | 是 | 项目 ID |
| search | string | 否 | 搜索关键词 |
| limit | integer | 否 | 每页数量，默认 100 |
| offset | integer | 否 | 偏移量，默认 0 |

**响应**:
```json
{
  "total": 1,
  "data": [
    {
      "id": 24,
      "project_id": 6,
      "section_code": "TEST-001",
      "section_name": "测试标段",
      "contractor_unit": "施工单位",
      "supervisor_unit": "监理单位",
      "designer_unit": "设计单位",
      "testing_unit": "检测单位",
      "created_at": "2025-11-07 07:29:23",
      "updated_at": "2025-11-07 07:29:23"
    }
  ]
}
```

---

### 获取单个标段

**请求**:
```http
GET /sections/{section_id}
```

**参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| section_id | integer | 是 | 标段 ID |

**响应**:
```json
{
  "id": 24,
  "project_id": 6,
  "section_code": "TEST-001",
  "section_name": "测试标段",
  "contractor_unit": "施工单位",
  "supervisor_unit": "监理单位",
  "designer_unit": "设计单位",
  "testing_unit": "检测单位",
  "created_at": "2025-11-07 07:29:23",
  "updated_at": "2025-11-07 07:29:23"
}
```

---

### 创建标段

**请求**:
```http
POST /sections?project_id=6&section_code=TEST-001&section_name=测试标段&...
```

**参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| project_id | integer | 是 | 项目 ID |
| section_code | string | 是 | 标段编号（1-100 字符） |
| section_name | string | 否 | 标段名称 |
| contractor_unit | string | 否 | 施工单位 |
| supervisor_unit | string | 否 | 监理单位 |
| designer_unit | string | 否 | 设计单位 |
| testing_unit | string | 否 | 第三方检测单位 |

**响应**:
```json
{
  "id": 24,
  "project_id": 6,
  "section_code": "TEST-001",
  "section_name": "测试标段",
  "contractor_unit": "施工单位",
  "supervisor_unit": "监理单位",
  "designer_unit": "设计单位",
  "testing_unit": "检测单位",
  "message": "标段创建成功"
}
```

---

### 修改标段

**请求**:
```http
PUT /sections/{section_id}?section_code=MODIFIED-001&...
```

**参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| section_id | integer | 是 | 标段 ID |
| section_code | string | 是 | 标段编号 |
| section_name | string | 否 | 标段名称 |
| contractor_unit | string | 否 | 施工单位 |
| supervisor_unit | string | 否 | 监理单位 |
| designer_unit | string | 否 | 设计单位 |
| testing_unit | string | 否 | 第三方检测单位 |

**响应**:
```json
{
  "id": 24,
  "project_id": 6,
  "section_code": "MODIFIED-001",
  "section_name": "修改后的标段",
  "contractor_unit": "修改后的施工单位",
  "supervisor_unit": "修改后的监理单位",
  "designer_unit": "修改后的设计单位",
  "testing_unit": "修改后的检测单位",
  "message": "标段修改成功"
}
```

---

### 删除标段

**请求**:
```http
DELETE /sections/{section_id}
```

**参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| section_id | integer | 是 | 标段 ID |

**响应**:
```json
{
  "success": true,
  "message": "标段删除成功"
}
```

---

## 🔄 使用示例

### 使用 curl

```bash
# 获取项目列表
curl "http://localhost:8000/api/projects"

# 创建项目
curl -X POST "http://localhost:8000/api/projects" \
  -H "Content-Type: application/json" \
  -d '{"project_name": "新项目", "builder_unit": "建设单位"}'

# 获取项目的标段列表
curl "http://localhost:8000/api/projects/1/sections"

# 创建标段
curl -X POST "http://localhost:8000/api/sections" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "section_code": "QFSG-1",
    "section_name": "标段 1",
    "contractor_unit": "施工单位"
  }'
```

### 使用 Python

```python
import requests

BASE_URL = "http://localhost:8000/api"

# 获取项目列表
response = requests.get(f"{BASE_URL}/projects")
projects = response.json()

# 创建项目
response = requests.post(
    f"{BASE_URL}/projects",
    params={
        "project_name": "新项目",
        "builder_unit": "建设单位"
    }
)
new_project = response.json()
```

---

**最后更新**: 2025-11-07


