# 🔧 故障排除指南

## 常见问题和解决方案

---

## 1️⃣ Node.js 版本过低

### 问题症状
```
Error [ERR_REQUIRE_ESM]: Must use import to load ES Module
```

### 原因
Vite 需要 Node.js 18.0.0 或更高版本，但您的系统安装的是 Node.js v12.16.1

### 解决方案

#### 方案 A: 使用 nvm 升级 Node.js（推荐）

**1. 安装 nvm**:
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
```

**2. 重新加载 shell 配置**:
```bash
source ~/.bashrc
# 或
source ~/.zshrc
```

**3. 安装 Node.js 18 LTS**:
```bash
nvm install 18
nvm use 18
```

**4. 验证版本**:
```bash
node --version  # 应该显示 v18.x.x 或更高
```

#### 方案 B: 直接从官网下载

访问 [https://nodejs.org/](https://nodejs.org/) 下载 LTS 版本（18.x 或 20.x）

#### 方案 C: 使用 Homebrew（Mac）

```bash
brew install node@18
brew link node@18
```

---

## 2️⃣ openpyxl 版本不存在

### 问题症状
```
ERROR: No matching distribution found for openpyxl==3.11.0
```

### 原因
`openpyxl==3.11.0` 版本不存在，最新版本是 3.1.5

### 解决方案

已在 `backend/requirements.txt` 中修复，将版本改为 `3.1.5`

如果仍然出现问题，请手动更新：

```bash
cd backend
pip install openpyxl==3.1.5
```

---

## 3️⃣ 后端依赖安装失败

### 问题症状
```
ERROR: Could not find a version that satisfies the requirement...
```

### 解决方案

**1. 清除 pip 缓存**:
```bash
pip cache purge
```

**2. 升级 pip**:
```bash
pip install --upgrade pip
```

**3. 重新安装依赖**:
```bash
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

---

## 4️⃣ 前端依赖安装失败

### 问题症状
```
npm ERR! code ERESOLVE
npm ERR! ERESOLVE unable to resolve dependency tree
```

### 解决方案

**1. 清除 npm 缓存**:
```bash
npm cache clean --force
```

**2. 删除 node_modules 和 package-lock.json**:
```bash
cd frontend
rm -rf node_modules package-lock.json
```

**3. 重新安装依赖**:
```bash
npm install
```

---

## 5️⃣ 端口被占用

### 问题症状
```
Error: listen EADDRINUSE: address already in use :::8000
```

### 解决方案

**查找占用端口的进程**:

**Linux/Mac**:
```bash
lsof -i :8000  # 查找占用 8000 端口的进程
kill -9 <PID>  # 杀死进程
```

**Windows**:
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**或者修改端口**:

编辑 `start-dev.sh` 或 `start-dev.bat`，将 `8000` 改为其他端口（如 `8001`）

---

## 6️⃣ 后端服务无法启动

### 问题症状
```
/usr/bin/python3: No module named uvicorn
```

### 解决方案

**1. 确保虚拟环境已激活**:
```bash
cd backend
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

**2. 重新安装 uvicorn**:
```bash
pip install uvicorn==0.24.0
```

**3. 手动启动后端**:
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 7️⃣ 前端无法连接到后端 API

### 问题症状
```
Failed to fetch from http://localhost:8000/api/...
CORS error
```

### 解决方案

**1. 确保后端服务正在运行**:
```bash
curl http://localhost:8000/docs
```

**2. 检查 API 代理配置**:

编辑 `frontend/vite.config.js`，确保代理配置正确：

```javascript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '/api'),
    },
  },
}
```

**3. 清除浏览器缓存**:
- 按 F12 打开开发者工具
- 右键点击刷新按钮，选择"清空缓存并硬性重新加载"

---

## 8️⃣ 数据库文件丢失

### 问题症状
```
sqlite3.OperationalError: unable to open database file
```

### 解决方案

**1. 检查数据库文件**:
```bash
ls -la backend/app/cdrl.db
```

**2. 如果文件不存在，重新创建**:
```bash
cd backend
python -c "from app.main import init_db; init_db()"
```

**3. 或者从备份恢复**:
```bash
cp backend/app/cdrl.db.backup backend/app/cdrl.db
```

---

## 9️⃣ 手动启动应用

如果启动脚本出现问题，可以手动启动：

### 启动后端

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 启动前端（新终端）

```bash
cd frontend
npm install
npm run dev
```

---

## 🔟 获取更多帮助

### 查看日志

**后端日志**:
```bash
tail -f /tmp/backend.log
```

**前端日志**:
查看浏览器开发者工具的 Console 标签

### 检查依赖版本

**Python 依赖**:
```bash
pip list
```

**Node.js 依赖**:
```bash
npm list
```

### 重置项目

如果问题无法解决，可以尝试完全重置：

```bash
# 删除虚拟环境
rm -rf backend/venv

# 删除 node_modules
rm -rf frontend/node_modules frontend/package-lock.json

# 重新启动
./start-dev.sh
```

---

## 📞 常用命令

| 命令 | 说明 |
|------|------|
| `node --version` | 查看 Node.js 版本 |
| `npm --version` | 查看 npm 版本 |
| `python3 --version` | 查看 Python 版本 |
| `pip list` | 列出已安装的 Python 包 |
| `npm list` | 列出已安装的 npm 包 |
| `npm cache clean --force` | 清除 npm 缓存 |
| `pip cache purge` | 清除 pip 缓存 |

---

## 💡 最佳实践

1. **定期更新依赖**:
   ```bash
   npm update
   pip install --upgrade -r requirements.txt
   ```

2. **使用虚拟环境**:
   - 后端: 使用 Python venv
   - 前端: 使用 node_modules

3. **检查版本兼容性**:
   - Node.js: 18.0.0+
   - Python: 3.8+
   - npm: 6.0.0+

4. **定期清理缓存**:
   ```bash
   npm cache clean --force
   pip cache purge
   ```

---

## 📝 反馈

如果遇到其他问题，请：
1. 查看完整的错误信息
2. 检查日志文件
3. 尝试重新安装依赖
4. 参考本指南中的解决方案

祝您使用愉快！🚀

