# 🚀 快速启动指南

## ⚡ 最快启动方式（一键启动）

### macOS / Linux
```bash
cd /Users/haolu/Library/CloudStorage/OneDrive-个人/进行中的工作/工程监督/AppDev/CDRLApp
./start.sh
```

### Windows
```bash
cd path\to\CDRLApp
start.bat
```

---

## 📋 手动启动（分步骤）

### 终端 1：启动后端
```bash
cd backend
python3 -m uvicorn app.main:app --reload --port 8000
```

**预期输出**：
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### 终端 2：启动前端
```bash
cd frontend
npm run dev
```

**预期输出**：
```
VITE v7.2.0  ready in 298 ms
  ➜  Local:   http://localhost:3001/
```

---

## 🌐 访问应用

打开浏览器访问：
```
http://localhost:3001
```

---

## 📊 服务地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端应用 | http://localhost:3001 | 主应用 |
| 后端 API | http://localhost:8000 | API 服务 |
| API 文档 | http://localhost:8000/docs | Swagger 文档 |
| 数据库 | backend/cdrl.db | SQLite 数据库 |

---

## 🛑 停止程序

```bash
# 在终端按 Ctrl+C 停止服务
Ctrl+C
```

---

## 🔄 重启程序

```bash
# 停止所有服务（Ctrl+C）
# 然后重新运行启动命令
```

---

## ⚙️ 常见命令

```bash
# 安装前端依赖
cd frontend && npm install

# 安装后端依赖
cd backend && pip install -r requirements.txt

# 构建前端生产版本
cd frontend && npm run build

# 查看后端 API 文档
# 打开浏览器访问 http://localhost:8000/docs
```

---

## 🐛 常见问题

### 端口被占用
```bash
# 查找占用端口的进程
lsof -i :8000  # 后端
lsof -i :3001  # 前端

# 杀死进程
kill -9 <PID>
```

### Node.js 版本过低
```bash
# 检查版本
node --version

# 需要 18.0.0 或更高版本
# 使用 nvm 升级
nvm install 18
nvm use 18
```

### Python 依赖缺失
```bash
cd backend
pip install -r requirements.txt
```

### 数据库初始化
```bash
cd backend
python3 << 'EOF'
from app.database import init_db
init_db()
print("数据库已初始化")
EOF
```

---

## ✅ 启动检查清单

- [ ] 后端运行在 http://localhost:8000
- [ ] 前端运行在 http://localhost:3001
- [ ] 浏览器可以访问应用
- [ ] 左侧菜单显示所有功能
- [ ] 没有浏览器控制台错误

---

## 📚 详细文档

查看完整的启动指南：
```bash
cat STARTUP_GUIDE.md
```

---

**最后更新**: 2025-11-07

