# 📝 Node.js 升级指南

## 当前状态

- **当前版本**: v12.16.1
- **需要版本**: v18.0.0 或更高
- **系统**: macOS (Apple Silicon - arm64)

---

## 🚀 升级方案

### 方案 1: 使用本地安装脚本（推荐）

这个方案不需要 sudo 权限，安装到本地目录。

**步骤 1: 运行升级脚本**

在 VSCode 终端中执行：

```bash
chmod +x upgrade-nodejs-local.sh
./upgrade-nodejs-local.sh
```

脚本会：
- 下载 Node.js 18.20.4
- 安装到 `~/.local/nodejs`
- 显示配置 PATH 的说明

**步骤 2: 配置 PATH**

脚本完成后，需要配置环境变量。编辑 `~/.zshrc` 文件：

```bash
nano ~/.zshrc
```

在文件末尾添加以下行：

```bash
export PATH="$HOME/.local/nodejs/bin:$PATH"
```

保存文件：
- 按 `Ctrl+O` 保存
- 按 `Enter` 确认
- 按 `Ctrl+X` 退出

**步骤 3: 重新加载配置**

```bash
source ~/.zshrc
```

**步骤 4: 验证安装**

```bash
node --version    # 应该显示 v18.20.4
npm --version     # 应该显示 9.x.x
```

---

### 方案 2: 使用 Homebrew（如果可用）

如果 Homebrew 正常工作，可以使用：

```bash
brew install node@18
brew link node@18
```

然后验证：

```bash
node --version
```

---

### 方案 3: 从官网下载

访问 [https://nodejs.org/](https://nodejs.org/) 下载 Node.js 18 LTS 版本。

**对于 Apple Silicon Mac (M1/M2/M3):**
- 下载 `node-v18.x.x-darwin-arm64.pkg`

**对于 Intel Mac:**
- 下载 `node-v18.x.x-darwin-x64.pkg`

然后运行安装程序，按照提示完成安装。

---

## ✅ 升级后的步骤

### 1. 重新启动终端

关闭 VSCode 终端，重新打开一个新的终端窗口。

### 2. 验证新版本

```bash
node --version    # 应该显示 v18.x.x 或更高
npm --version     # 应该显示 9.x.x 或更高
```

### 3. 清除前端缓存

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### 4. 启动应用

```bash
cd ..
./start-dev.sh
```

---

## 🔍 故障排除

### 问题 1: 升级后仍显示旧版本

**原因**: PATH 配置问题

**解决方案**:

```bash
# 检查 PATH
echo $PATH

# 查看 node 的位置
which node

# 如果显示旧版本的路径，需要重新配置 PATH
# 编辑 ~/.zshrc 并确保新版本的路径在最前面
nano ~/.zshrc

# 重新加载配置
source ~/.zshrc
```

### 问题 2: npm 命令找不到

**原因**: npm 没有正确安装或 PATH 配置错误

**解决方案**:

```bash
# 检查 npm 位置
which npm

# 如果找不到，检查 Node.js 安装目录
ls ~/.local/nodejs/bin/

# 确保 PATH 配置正确
echo $PATH | grep nodejs
```

### 问题 3: 前端仍然无法启动

**原因**: node_modules 缓存问题

**解决方案**:

```bash
cd frontend
rm -rf node_modules package-lock.json .vite dist
npm cache clean --force
npm install
npm run dev
```

---

## 📊 版本检查

升级完成后，运行以下命令验证所有版本：

```bash
echo "=== 版本检查 ==="
echo "Node.js: $(node --version)"
echo "npm: $(npm --version)"
echo "Python: $(python3 --version)"
echo ""
echo "=== 路径检查 ==="
echo "node 位置: $(which node)"
echo "npm 位置: $(which npm)"
echo "python3 位置: $(which python3)"
```

---

## 💡 建议

1. **定期更新**: 定期检查并更新 Node.js 和 npm
   ```bash
   npm install -g npm@latest
   ```

2. **使用版本管理器**: 考虑使用 nvm 或 fnm 来管理多个 Node.js 版本

3. **清理缓存**: 定期清理 npm 缓存
   ```bash
   npm cache clean --force
   ```

4. **备份**: 升级前备份重要文件

---

## 📞 获取帮助

如果升级过程中遇到问题：

1. 查看 `TROUBLESHOOTING.md` 获取更多帮助
2. 查看 `upgrade-nodejs-local.sh` 脚本的详细说明
3. 访问 [Node.js 官网](https://nodejs.org/) 获取最新信息

---

## ✨ 升级完成

升级完成后，您可以：

1. 运行 `./start-dev.sh` 启动应用
2. 访问 http://localhost:3000 查看前端应用
3. 访问 http://localhost:8000/docs 查看 API 文档

祝您使用愉快！🚀

