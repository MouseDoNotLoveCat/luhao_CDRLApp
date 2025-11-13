# CDRLApp 启动程序指南

## 📋 前置要求

### 系统要求
- **操作系统**: macOS / Linux / Windows
- **Node.js**: 18.0.0 或更高版本
- **Python**: 3.8 或更高版本
- **SQLite**: 已包含在 Python 中

### 检查环境
```bash
# 检查 Node.js 版本
node --version

# 检查 Python 版本
python3 --version
```

---

## 🚀 快速启动（推荐）

### 方式 1：使用脚本启动（最简单）

#### macOS / Linux
```bash
# 进入项目根目录
cd /Users/haolu/Library/CloudStorage/OneDrive-个人/进行中的工作/工程监督/AppDev/CDRLApp

# 启动后端和前端
./start.sh
```

#### Windows
```bash
# 进入项目根目录
cd path\to\CDRLApp

# 启动后端和前端
start.bat
```

---

## 🔧 手动启动（分步骤）

### 步骤 1：启动后端服务

#### 打开第一个终端窗口
```bash
# 进入后端目录
cd backend

# 启动 FastAPI 服务器
python3 -m uvicorn app.main:app --reload --port 8000
```

**预期输出**：
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

**后端服务地址**: http://localhost:8000

---

### 步骤 2：启动前端服务

#### 打开第二个终端窗口
```bash
# 进入前端目录
cd frontend

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev
```

**预期输出**：
```
VITE v7.2.0  ready in 298 ms

  ➜  Local:   http://localhost:3001/
  ➜  Network: use --host to expose
```

**前端应用地址**: http://localhost:3001

---

## 📱 访问应用

### 打开浏览器
```
http://localhost:3001
```

### 主要功能菜单
1. **📥 导入监督检查通知书** - 导入 Word 文档
2. **📋 通知书管理** - 查看已导入的通知书
3. **🔍 问题一览表** - 查看所有问题
4. **⚙️ 项目与标段管理** - 管理项目和标段

---

## 🛑 停止程序

### 停止后端服务
```bash
# 在后端终端窗口按 Ctrl+C
Ctrl+C
```

### 停止前端服务
```bash
# 在前端终端窗口按 Ctrl+C
Ctrl+C
```

---

## 🔄 重启程序

### 快速重启
```bash
# 停止所有服务（按 Ctrl+C）
# 然后重新运行启动命令
```

### 清除缓存后重启
```bash
# 清除前端缓存
cd frontend
rm -rf node_modules/.vite
npm run dev

# 清除后端缓存
cd backend
find . -type d -name __pycache__ -exec rm -r {} +
python3 -m uvicorn app.main:app --reload --port 8000
```

---

## 🐛 常见问题

### 问题 1：端口已被占用

**错误信息**：
```
Address already in use
```

**解决方案**：
```bash
# 查找占用端口的进程
lsof -i :8000  # 后端
lsof -i :3001  # 前端

# 杀死进程
kill -9 <PID>

# 或使用不同的端口
python3 -m uvicorn app.main:app --reload --port 8001
npm run dev -- --port 3002
```

### 问题 2：Node.js 版本过低

**错误信息**：
```
Node.js version is not compatible
```

**解决方案**：
```bash
# 升级 Node.js
# 使用 nvm (Node Version Manager)
nvm install 18
nvm use 18
```

### 问题 3：Python 依赖缺失

**错误信息**：
```
ModuleNotFoundError: No module named 'fastapi'
```

**解决方案**：
```bash
cd backend
pip install -r requirements.txt
```

### 问题 4：数据库文件丢失

**错误信息**：
```
sqlite3.OperationalError: unable to open database file
```

**解决方案**：
```bash
cd backend
python3 << 'EOF'
from app.database import init_db
init_db()
print("数据库已初始化")
EOF
```

---

## 📊 服务状态检查

### 检查后端服务
```bash
curl http://localhost:8000/api/projects
```

**预期响应**：
```json
{
  "total": 0,
  "data": []
}
```

### 检查前端服务
```bash
curl http://localhost:3001
```

**预期响应**：HTML 页面内容

---

## 🔐 开发模式 vs 生产模式

### 开发模式（当前使用）
```bash
# 后端：启用热重载
python3 -m uvicorn app.main:app --reload --port 8000

# 前端：启用热模块替换 (HMR)
npm run dev
```

**特点**：
- ✅ 代码修改自动重新加载
- ✅ 详细的错误信息
- ✅ 便于调试

### 生产模式（部署时使用）
```bash
# 后端：禁用热重载
python3 -m uvicorn app.main:app --port 8000

# 前端：构建生产版本
npm run build
npm run preview
```

**特点**：
- ✅ 性能优化
- ✅ 代码压缩
- ✅ 生产就绪

---

## 📝 日志查看

### 后端日志
```bash
# 日志文件位置
backend/logs/app.log

# 查看实时日志
tail -f backend/logs/app.log
```

### 前端日志
```bash
# 打开浏览器开发者工具
F12 或 Cmd+Option+I

# 查看 Console 标签页
```

---

## 🔗 有用的链接

| 资源 | 地址 |
|------|------|
| 前端应用 | http://localhost:3001 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |
| 数据库 | backend/cdrl.db |

---

## 💡 快速命令参考

```bash
# 启动后端
cd backend && python3 -m uvicorn app.main:app --reload --port 8000

# 启动前端
cd frontend && npm run dev

# 安装前端依赖
cd frontend && npm install

# 安装后端依赖
cd backend && pip install -r requirements.txt

# 运行后端测试
cd backend && python3 -m pytest

# 构建前端生产版本
cd frontend && npm run build

# 清除前端缓存
cd frontend && rm -rf node_modules dist .vite

# 清除后端缓存
cd backend && find . -type d -name __pycache__ -exec rm -r {} +
```

---

## ✅ 启动检查清单

启动后，请检查以下项目：

- [ ] 后端服务运行在 http://localhost:8000
- [ ] 前端应用运行在 http://localhost:3001
- [ ] 浏览器可以访问 http://localhost:3001
- [ ] 左侧菜单显示所有功能项
- [ ] 可以导入 Word 文档
- [ ] 可以查看通知书列表
- [ ] 可以查看问题详情
- [ ] 没有浏览器控制台错误

---

**最后更新**: 2025-11-07  
**版本**: 1.0.0

