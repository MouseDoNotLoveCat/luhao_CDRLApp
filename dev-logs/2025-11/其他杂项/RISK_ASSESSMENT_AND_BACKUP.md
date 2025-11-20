# 风险评估和备份方案

## 🚨 风险评估

### 1. 数据库迁移风险

| 风险 | 概率 | 影响 | 缓解方案 |
|------|------|------|---------|
| **迁移脚本执行失败** | 中 | 数据库损坏 | 完整备份 + 测试环境验证 |
| **数据丢失** | 低 | 现有问题无法恢复 | 使用 LEFT JOIN 保留所有数据 |
| **外键约束冲突** | 中 | 迁移中断 | 先禁用外键检查 |
| **索引丢失** | 低 | 查询性能下降 | 迁移后重建所有索引 |
| **应用启动失败** | 中 | 服务中断 | 回滚脚本 + 恢复备份 |

### 2. 代码修改风险

| 风险 | 概率 | 影响 | 缓解方案 |
|------|------|------|---------|
| **遗漏代码引用** | 中 | 运行时错误 | 全局搜索 `section_id` |
| **前端兼容性** | 低 | 界面显示错误 | 充分测试 |
| **API 不兼容** | 中 | 导入失败 | 版本控制 + 测试 |

### 3. 业务风险

| 风险 | 概率 | 影响 | 缓解方案 |
|------|------|------|---------|
| **用户数据混乱** | 低 | 数据不一致 | 迁移前通知用户 |
| **导入功能中断** | 中 | 无法导入新问题 | 充分测试 + 灰度发布 |

---

## 💾 备份方案

### 1. 备份前检查清单

```bash
# 检查数据库大小
sqlite3 backend/cdrl.db "SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size();"

# 检查现有问题数量
sqlite3 backend/cdrl.db "SELECT COUNT(*) FROM issues;"

# 检查现有标段数量
sqlite3 backend/cdrl.db "SELECT COUNT(*) FROM sections;"

# 检查数据库完整性
sqlite3 backend/cdrl.db "PRAGMA integrity_check;"
```

### 2. 备份步骤

#### 步骤 1：创建完整备份

```bash
# 创建备份目录
mkdir -p backups/$(date +%Y%m%d_%H%M%S)

# 备份数据库文件
cp backend/cdrl.db backups/$(date +%Y%m%d_%H%M%S)/cdrl.db.backup

# 备份数据库 SQL 导出
sqlite3 backend/cdrl.db ".dump" > backups/$(date +%Y%m%d_%H%M%S)/cdrl_dump.sql

# 备份迁移前的表结构
sqlite3 backend/cdrl.db ".schema issues" > backups/$(date +%Y%m%d_%H%M%S)/issues_schema_before.sql
sqlite3 backend/cdrl.db ".schema sections" > backups/$(date +%Y%m%d_%H%M%S)/sections_schema_before.sql
```

#### 步骤 2：验证备份

```bash
# 验证备份文件大小
ls -lh backups/$(date +%Y%m%d_%H%M%S)/

# 验证 SQL 导出的完整性
grep -c "INSERT INTO issues" backups/$(date +%Y%m%d_%H%M%S)/cdrl_dump.sql

# 验证备份数据库可以打开
sqlite3 backups/$(date +%Y%m%d_%H%M%S)/cdrl.db.backup "SELECT COUNT(*) FROM issues;"
```

### 3. 回滚方案

#### 快速回滚（< 1 分钟）

```bash
# 停止应用
pkill -f "uvicorn"

# 恢复备份
cp backups/$(date +%Y%m%d_%H%M%S)/cdrl.db.backup backend/cdrl.db

# 重启应用
cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
```

#### 完整回滚（包括代码）

```bash
# 1. 恢复数据库
cp backups/$(date +%Y%m%d_%H%M%S)/cdrl.db.backup backend/cdrl.db

# 2. 恢复代码
git checkout HEAD -- backend/app/services/import_service.py
git checkout HEAD -- database_schema.sql

# 3. 重启应用
pkill -f "uvicorn"
cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
```

---

## 🧪 测试计划

### 1. 单元测试

```python
# 测试迁移脚本
def test_migration_script():
    # 1. 创建测试数据库
    # 2. 执行迁移脚本
    # 3. 验证表结构
    # 4. 验证数据完整性
    pass

# 测试 _insert_issue 方法
def test_insert_issue_without_section_id():
    # 1. 创建测试数据
    # 2. 调用 _insert_issue
    # 3. 验证问题是否正确插入
    # 4. 验证 section_name 是否正确保存
    pass
```

### 2. 集成测试

```python
# 测试完整导入流程
def test_import_workflow():
    # 1. 上传 Word 文档
    # 2. 识别问题
    # 3. 选择问题
    # 4. 导入问题
    # 5. 验证数据库中的问题
    pass
```

### 3. 手动测试清单

- [ ] 导入新的 Word 文档
- [ ] 验证问题是否正确导入
- [ ] 验证标段名称是否正确保存
- [ ] 验证现有问题查询功能
- [ ] 验证问题详情页面
- [ ] 验证问题编辑功能
- [ ] 验证问题删除功能

---

## 📋 迁移执行清单

### 迁移前

- [ ] 备份数据库
- [ ] 验证备份完整性
- [ ] 通知用户停止使用系统
- [ ] 停止后端应用
- [ ] 检查是否有正在进行的导入操作

### 迁移中

- [ ] 禁用外键检查
- [ ] 执行迁移脚本
- [ ] 验证表结构
- [ ] 验证数据完整性
- [ ] 重建索引
- [ ] 启用外键检查

### 迁移后

- [ ] 修改后端代码
- [ ] 修改前端代码
- [ ] 启动后端应用
- [ ] 启动前端应用
- [ ] 执行集成测试
- [ ] 验证导入功能
- [ ] 通知用户系统恢复

---

## 🔍 验证脚本

### 迁移前验证

```bash
#!/bin/bash
echo "=== 迁移前验证 ==="
echo "1. 检查数据库完整性..."
sqlite3 backend/cdrl.db "PRAGMA integrity_check;"

echo "2. 检查现有数据..."
echo "   问题数量: $(sqlite3 backend/cdrl.db 'SELECT COUNT(*) FROM issues;')"
echo "   标段数量: $(sqlite3 backend/cdrl.db 'SELECT COUNT(*) FROM sections;')"
echo "   通知书数量: $(sqlite3 backend/cdrl.db 'SELECT COUNT(*) FROM supervision_notices;')"

echo "3. 检查外键约束..."
sqlite3 backend/cdrl.db "PRAGMA foreign_key_list(issues);"
```

### 迁移后验证

```bash
#!/bin/bash
echo "=== 迁移后验证 ==="
echo "1. 检查表结构..."
sqlite3 backend/cdrl.db ".schema issues" | grep -E "section_name|section_id"

echo "2. 检查数据完整性..."
echo "   问题数量: $(sqlite3 backend/cdrl.db 'SELECT COUNT(*) FROM issues;')"
echo "   标段名称为空的问题: $(sqlite3 backend/cdrl.db 'SELECT COUNT(*) FROM issues WHERE section_name IS NULL;')"

echo "3. 检查索引..."
sqlite3 backend/cdrl.db ".indexes issues"

echo "4. 检查外键约束..."
sqlite3 backend/cdrl.db "PRAGMA foreign_key_list(issues);"
```

---

## 📞 应急联系

如果迁移失败：

1. **立即停止应用**
   ```bash
   pkill -f "uvicorn"
   ```

2. **恢复备份**
   ```bash
   cp backups/YYYYMMDD_HHMMSS/cdrl.db.backup backend/cdrl.db
   ```

3. **重启应用**
   ```bash
   cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
   ```

4. **检查日志**
   ```bash
   tail -f /tmp/backend.log
   ```


