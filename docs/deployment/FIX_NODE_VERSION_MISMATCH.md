# 🔧 Node.js 版本不一致问题解决方案

## 问题描述

您已经安装了 Node.js v24.11.0，但启动脚本仍然检测到 v12.16.1，导致前端启动失败。

**症状**:
- 手动运行 `node --version` 显示 v24.11.0 ✅
- 启动脚本显示 v12.16.1 ❌
- 前端启动失败: `Error [ERR_REQUIRE_ESM]`

**根本原因**: 启动脚本在子 shell 中运行，没有加载 nvm 的环境配置。

---

## 🚀 快速解决方案

### 方案 1: 使用新的 nvm 专用启动脚本（推荐）

```bash
chmod +x start-dev-nvm.sh
./start-dev-nvm.sh
```

这个脚本会：
1. ✅ 自动加载 nvm 环境
2. ✅ 检查 Node.js 版本
3. ✅ 启动后端和前端服务
4. ✅ 正确处理进程清理

---

## 🔍 诊断步骤

### 步骤 1: 运行诊断脚本

```bash
chmod +x diagnose-nodejs.sh
./diagnose-nodejs.sh
```

这个脚本会检查：
- ✅ nvm 是否正确安装
- ✅ Node.js 版本
- ✅ PATH 环境变量
- ✅ Shell 配置文件
- ✅ 旧版本 Node.js 位置

### 步骤 2: 查看诊断结果

根据诊断结果，选择相应的解决方案。

---

## 🛠️ 详细解决方案

### 问题 1: nvm 环境未加载

**症状**: 脚本显示 Node.js 版本过低

**解决方案**:

```bash
# 1. 检查 nvm 是否安装
ls -la ~/.nvm

# 2. 加载 nvm
source ~/.nvm/nvm.sh

# 3. 验证
node --version  # 应该显示 v24.11.0

# 4. 使用新脚本启动
./start-dev-nvm.sh
```

---

### 问题 2: PATH 配置错误

**症状**: 系统使用了旧版本的 Node.js

**解决方案**:

```bash
# 1. 检查 PATH
echo $PATH

# 2. 检查 node 的位置
which node

# 3. 如果显示 /usr/local/bin/node，需要调整 PATH
# 编辑 ~/.zshrc 或 ~/.bashrc

nano ~/.zshrc

# 4. 确保 nvm 的路径在最前面
# 添加或修改以下行（在文件末尾）:
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 5. 保存并重新加载
source ~/.zshrc

# 6. 验证
node --version
```

---

### 问题 3: 旧版本 Node.js 干扰

**症状**: 即使配置了 PATH，仍然使用旧版本

**解决方案**:

```bash
# 1. 找到旧版本的位置
which node

# 2. 检查所有可能的位置
ls -la /usr/local/bin/node*
ls -la /usr/bin/node*
ls -la /opt/homebrew/bin/node*

# 3. 删除或重命名旧版本（需要 sudo）
sudo mv /usr/local/bin/node /usr/local/bin/node.old
sudo mv /usr/local/bin/npm /usr/local/bin/npm.old

# 4. 验证
node --version  # 应该显示 v24.11.0
```

---

## 📋 完整步骤指南

### 第一次使用（完整设置）

```bash
# 1. 运行诊断脚本
chmod +x diagnose-nodejs.sh
./diagnose-nodejs.sh

# 2. 根据诊断结果，修复 PATH（如果需要）
nano ~/.zshrc

# 3. 重新加载 shell 配置
source ~/.zshrc

# 4. 验证 Node.js 版本
node --version    # 应该显示 v24.11.0 或更高
npm --version

# 5. 使用新脚本启动应用
chmod +x start-dev-nvm.sh
./start-dev-nvm.sh
```

### 后续使用

```bash
# 直接使用新脚本启动
./start-dev-nvm.sh
```

---

## 🔄 更新的启动脚本

### start-dev.sh（已更新）

已更新以自动加载 nvm 环境：

```bash
# 加载 nvm 环境（如果已安装）
export NVM_DIR="$HOME/.nvm"
if [ -s "$NVM_DIR/nvm.sh" ]; then
    source "$NVM_DIR/nvm.sh"
fi
```

### start-dev-nvm.sh（新增）

专门为 nvm 用户设计的启动脚本，包含：
- ✅ 自动加载 nvm
- ✅ 版本检查
- ✅ 错误处理
- ✅ 进程清理

---

## ✅ 验证解决方案

### 检查清单

- [ ] 运行 `node --version` 显示 v24.11.0 或更高
- [ ] 运行 `npm --version` 显示 9.x.x 或更高
- [ ] 运行 `./start-dev-nvm.sh` 成功启动
- [ ] 前端应用在 http://localhost:3000 可访问
- [ ] 后端 API 在 http://localhost:8000 可访问

### 测试命令

```bash
# 1. 验证版本
node --version
npm --version

# 2. 运行诊断
./diagnose-nodejs.sh

# 3. 启动应用
./start-dev-nvm.sh

# 4. 访问应用
# 前端: http://localhost:3000
# 后端: http://localhost:8000/docs
```

---

## 📞 常见问题

**Q: 为什么需要两个启动脚本？**
A: `start-dev.sh` 是通用脚本，`start-dev-nvm.sh` 是专为 nvm 用户优化的脚本，提供更好的错误处理和版本检查。

**Q: 可以删除旧版本的 Node.js 吗？**
A: 可以，但建议先备份。使用 `sudo mv /usr/local/bin/node /usr/local/bin/node.old` 重命名而不是删除。

**Q: 如何切换 Node.js 版本？**
A: 使用 `nvm use 24` 切换到 v24，使用 `nvm use 18` 切换到 v18。

**Q: 如何设置默认 Node.js 版本？**
A: 使用 `nvm alias default 24` 设置默认版本。

---

## 🎯 下一步

1. ✅ 运行诊断脚本: `./diagnose-nodejs.sh`
2. ✅ 根据诊断结果修复问题
3. ✅ 使用新脚本启动: `./start-dev-nvm.sh`
4. ✅ 验证应用正常运行

祝您使用愉快！🚀

