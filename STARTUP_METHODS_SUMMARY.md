# 📚 CDRLApp 启动程序方式总结

## 📋 文档清单

本项目提供了多种启动方式和详细的文档：

### 📖 主要文档

| 文档 | 说明 | 适用场景 |
|------|------|---------|
| **QUICK_START.md** | 快速启动指南 | 快速上手，常用命令 |
| **STARTUP_GUIDE.md** | 完整启动指南 | 详细说明，故障排查 |
| **STARTUP_METHODS_SUMMARY.md** | 本文档 | 启动方式总结 |

---

## 🚀 启动方式对比

### 方式 1：一键启动脚本（推荐）

#### 优点
- ✅ 最简单快速
- ✅ 自动检查环境
- ✅ 自动安装依赖
- ✅ 一条命令启动所有服务

#### 缺点
- ❌ 需要 bash/cmd 支持
- ❌ 不能单独控制后端/前端

#### 使用方法

**macOS / Linux**：
```bash
./start.sh
```

**Windows**：
```bash
start.bat
```

#### 预期结果
```
✅ 所有服务已启动
📱 前端应用: http://localhost:3001
🔌 后端 API: http://localhost:8000
```

---

### 方式 2：手动启动（推荐用于开发）

#### 优点
- ✅ 灵活控制
- ✅ 可单独启动/停止
- ✅ 便于调试
- ✅ 可查看详细日志

#### 缺点
- ❌ 需要打开多个终端
- ❌ 需要手动执行命令

#### 使用方法

**终端 1 - 启动后端**：
```bash
cd backend
python3 -m uvicorn app.main:app --reload --port 8000
```

**终端 2 - 启动前端**：
```bash
cd frontend
npm run dev
```

#### 预期结果
```
后端: INFO:     Uvicorn running on http://127.0.0.1:8000
前端: ➜  Local:   http://localhost:3001/
```

---

### 方式 3：使用 npm 脚本

#### 优点
- ✅ 简洁
- ✅ 易于记忆

#### 缺点
- ❌ 需要在前端目录执行
- ❌ 只启动前端

#### 使用方法

```bash
cd frontend
npm run dev
```

---

### 方式 4：使用 Python 直接运行

#### 优点
- ✅ 最直接
- ✅ 完全控制

#### 缺点
- ❌ 需要手动管理依赖
- ❌ 需要激活虚拟环境

#### 使用方法

```bash
cd backend
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate.bat  # Windows

python3 -m uvicorn app.main:app --reload --port 8000
```

---

## 🎯 选择建议

### 场景 1：首次启动
**推荐**：方式 1（一键启动脚本）
```bash
./start.sh  # macOS/Linux
start.bat   # Windows
```

### 场景 2：日常开发
**推荐**：方式 2（手动启动）
- 便于调试
- 可单独重启服务
- 可查看详细日志

### 场景 3：只修改前端
**推荐**：方式 3（npm 脚本）
```bash
cd frontend && npm run dev
```

### 场景 4：只修改后端
**推荐**：方式 4（Python 直接运行）
```bash
cd backend && python3 -m uvicorn app.main:app --reload --port 8000
```

---

## 📊 启动流程图

```
开始
  ↓
选择启动方式
  ├─→ 一键启动 (start.sh/start.bat)
  │     ↓
  │   检查环境 → 安装依赖 → 启动后端 → 启动前端 → 完成
  │
  ├─→ 手动启动
  │     ↓
  │   终端1: 启动后端
  │   终端2: 启动前端
  │     ↓
  │   完成
  │
  └─→ 其他方式
        ↓
      完成
```

---

## ✅ 启动检查清单

启动后，请验证以下项目：

- [ ] 后端服务运行在 http://localhost:8000
- [ ] 前端应用运行在 http://localhost:3001
- [ ] 浏览器可以访问 http://localhost:3001
- [ ] 左侧菜单显示所有功能项
- [ ] 没有浏览器控制台错误
- [ ] 可以导入 Word 文档
- [ ] 可以查看通知书列表

---

## 🛑 停止程序

### 方式 1：一键启动脚本
```bash
# 在脚本窗口按 Ctrl+C
Ctrl+C
```

### 方式 2：手动启动
```bash
# 在每个终端窗口按 Ctrl+C
Ctrl+C
```

---

## 🔄 重启程序

### 快速重启
```bash
# 停止所有服务（Ctrl+C）
# 然后重新运行启动命令
```

### 清除缓存后重启
```bash
# 清除前端缓存
cd frontend && rm -rf node_modules/.vite

# 清除后端缓存
cd backend && find . -type d -name __pycache__ -exec rm -r {} +

# 重新启动
./start.sh  # 或其他启动方式
```

---

## 🐛 常见问题

### Q1：端口被占用怎么办？
```bash
# 查找占用端口的进程
lsof -i :8000  # 后端
lsof -i :3001  # 前端

# 杀死进程
kill -9 <PID>
```

### Q2：Node.js 版本过低怎么办？
```bash
# 检查版本
node --version

# 需要 18.0.0 或更高版本
# 使用 nvm 升级
nvm install 18
nvm use 18
```

### Q3：Python 依赖缺失怎么办？
```bash
cd backend
pip install -r requirements.txt
```

### Q4：数据库初始化失败怎么办？
```bash
cd backend
python3 << 'EOF'
from app.database import init_db
init_db()
print("数据库已初始化")
EOF
```

---

## 📚 相关文档

- [快速启动指南](QUICK_START.md) - 快速上手
- [完整启动指南](STARTUP_GUIDE.md) - 详细说明
- [测试指南](TESTING_GUIDE.md) - 测试方法

---

## 🔗 有用的链接

| 资源 | 地址 |
|------|------|
| 前端应用 | http://localhost:3001 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |
| 数据库 | backend/cdrl.db |

---

**最后更新**: 2025-11-07  
**版本**: 1.0.0

