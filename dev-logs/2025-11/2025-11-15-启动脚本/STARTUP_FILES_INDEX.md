# 📑 CDRLApp 启动程序文件索引

## 📂 启动脚本文件

### 一键启动脚本

| 文件 | 系统 | 说明 | 使用方法 |
|------|------|------|---------|
| `start.sh` | macOS/Linux | 自动启动后端和前端 | `./start.sh` |
| `start.bat` | Windows | 自动启动后端和前端 | `start.bat` |

### 开发启动脚本

| 文件 | 系统 | 说明 | 使用方法 |
|------|------|------|---------|
| `start-dev.sh` | macOS/Linux | 开发模式启动 | `./start-dev.sh` |
| `start-dev.bat` | Windows | 开发模式启动 | `start-dev.bat` |
| `start-dev-nvm.sh` | macOS/Linux | 使用 nvm 启动 | `./start-dev-nvm.sh` |

---

## 📚 启动文档

### 快速参考

| 文档 | 大小 | 说明 | 适用场景 |
|------|------|------|---------|
| **QUICK_START.md** | 📄 小 | 快速启动指南 | 快速上手 |
| **STARTUP_VISUAL_GUIDE.md** | 📄 小 | 可视化启动指南 | 可视化学习 |

### 详细指南

| 文档 | 大小 | 说明 | 适用场景 |
|------|------|------|---------|
| **STARTUP_GUIDE.md** | 📖 大 | 完整启动指南 | 详细说明、故障排查 |
| **STARTUP_METHODS_SUMMARY.md** | 📖 中 | 启动方式总结 | 方式对比、选择建议 |

### 本文档

| 文档 | 说明 |
|------|------|
| **STARTUP_FILES_INDEX.md** | 启动文件索引（本文档） |

---

## 🚀 快速导航

### 我想快速启动应用
👉 查看 [QUICK_START.md](QUICK_START.md)

```bash
./start.sh  # macOS/Linux
start.bat   # Windows
```

### 我想了解所有启动方式
👉 查看 [STARTUP_METHODS_SUMMARY.md](STARTUP_METHODS_SUMMARY.md)

### 我想看可视化指南
👉 查看 [STARTUP_VISUAL_GUIDE.md](STARTUP_VISUAL_GUIDE.md)

### 我遇到了问题
👉 查看 [STARTUP_GUIDE.md](STARTUP_GUIDE.md) 的故障排查部分

### 我想了解详细信息
👉 查看 [STARTUP_GUIDE.md](STARTUP_GUIDE.md)

---

## 📋 启动方式对比

### 方式 1：一键启动（推荐）
```bash
./start.sh      # macOS/Linux
start.bat       # Windows
```
- ✅ 最简单
- ✅ 自动检查环境
- ✅ 自动安装依赖
- ⏱️ 首次启动 ~16-36 秒

### 方式 2：手动启动（推荐用于开发）
```bash
# 终端 1
cd backend
python3 -m uvicorn app.main:app --reload --port 8000

# 终端 2
cd frontend
npm run dev
```
- ✅ 灵活控制
- ✅ 便于调试
- ⏱️ 启动 ~5 秒

### 方式 3：开发脚本启动
```bash
./start-dev.sh      # macOS/Linux
start-dev.bat       # Windows
```
- ✅ 开发优化
- ✅ 自动配置
- ⏱️ 启动 ~10-20 秒

### 方式 4：使用 nvm 启动
```bash
./start-dev-nvm.sh  # macOS/Linux
```
- ✅ 自动管理 Node.js 版本
- ✅ 避免版本冲突
- ⏱️ 启动 ~10-20 秒

---

## 🎯 选择建议

| 场景 | 推荐方式 | 命令 |
|------|---------|------|
| 首次启动 | 一键启动 | `./start.sh` |
| 日常开发 | 手动启动 | 见上方 |
| 只修改前端 | npm 脚本 | `cd frontend && npm run dev` |
| 只修改后端 | Python 直接运行 | `cd backend && python3 -m uvicorn ...` |
| Node.js 版本问题 | nvm 启动 | `./start-dev-nvm.sh` |

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
# 在终端按 Ctrl+C
Ctrl+C
```

---

## 🔄 重启程序

```bash
# 停止所有服务（Ctrl+C）
# 然后重新运行启动命令
./start.sh  # 或其他启动方式
```

---

## ✅ 启动检查清单

启动后，请验证以下项目：

- [ ] 后端运行在 http://localhost:8000
- [ ] 前端运行在 http://localhost:3001
- [ ] 浏览器可以访问应用
- [ ] 左侧菜单显示所有功能
- [ ] 没有浏览器控制台错误
- [ ] 可以导入 Word 文档
- [ ] 可以查看通知书列表

---

## 🐛 常见问题快速链接

| 问题 | 文档位置 |
|------|---------|
| 端口被占用 | [STARTUP_GUIDE.md](STARTUP_GUIDE.md#问题-1端口已被占用) |
| Node.js 版本过低 | [STARTUP_GUIDE.md](STARTUP_GUIDE.md#问题-2nodejs-版本过低) |
| Python 依赖缺失 | [STARTUP_GUIDE.md](STARTUP_GUIDE.md#问题-3python-依赖缺失) |
| 数据库文件丢失 | [STARTUP_GUIDE.md](STARTUP_GUIDE.md#问题-4数据库文件丢失) |

---

## 📞 获取帮助

### 快速问题
查看 [QUICK_START.md](QUICK_START.md)

### 详细问题
查看 [STARTUP_GUIDE.md](STARTUP_GUIDE.md)

### 方式对比
查看 [STARTUP_METHODS_SUMMARY.md](STARTUP_METHODS_SUMMARY.md)

### 可视化学习
查看 [STARTUP_VISUAL_GUIDE.md](STARTUP_VISUAL_GUIDE.md)

---

## 📈 文档统计

| 类型 | 数量 | 总行数 |
|------|------|--------|
| 启动脚本 | 4 | ~500 |
| 启动文档 | 5 | ~1500 |
| 总计 | 9 | ~2000 |

---

## 🔗 相关文档

- [项目 README](README.md)
- [测试指南](TESTING_GUIDE.md)
- [完整启动指南](STARTUP_GUIDE.md)

---

**最后更新**: 2025-11-07  
**版本**: 1.0.0  
**状态**: ✅ 完成

