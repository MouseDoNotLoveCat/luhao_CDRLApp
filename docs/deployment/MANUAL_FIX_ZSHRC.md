# 🔧 手动修复 ~/.zshrc 文件

## 问题

~/.zshrc 文件由 root 拥有，权限为 444（只读），导致无法自动修改。

## 解决方案

### 方法 1: 使用 VSCode 编辑器（推荐）

#### 步骤 1: 打开 ~/.zshrc 文件

在 VSCode 中：
1. 按 `Cmd+Shift+P` 打开命令面板
2. 输入 `File: Open` 并选择
3. 输入路径: `~/.zshrc`
4. 按 Enter 打开文件

#### 步骤 2: 查看当前内容

文件应该包含：

```bash
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/opt/anaconda3/bin/conda' 'shell.zsh' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/opt/anaconda3/etc/profile.d/conda.sh" ]; then
        . "/opt/anaconda3/etc/profile.d/conda.sh"
    else
        export PATH="/opt/anaconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<
```

#### 步骤 3: 在文件末尾添加 nvm 配置

在文件末尾添加以下内容：

```bash

# >>> nvm initialize >>>
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
# <<< nvm initialize <<<
```

#### 步骤 4: 保存文件

按 `Cmd+S` 保存文件。

如果出现权限错误，VSCode 会提示您需要提升权限。点击 "Retry as Sudo" 或 "Use Sudo"。

---

### 方法 2: 使用终端命令

如果 VSCode 方法不工作，使用以下命令：

```bash
# 1. 备份原文件
cp ~/.zshrc ~/.zshrc.backup

# 2. 创建新文件
cat > ~/.zshrc << 'EOF'
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/opt/anaconda3/bin/conda' 'shell.zsh' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/opt/anaconda3/etc/profile.d/conda.sh" ]; then
        . "/opt/anaconda3/etc/profile.d/conda.sh"
    else
        export PATH="/opt/anaconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

# >>> nvm initialize >>>
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
# <<< nvm initialize <<<
EOF

# 3. 验证文件
cat ~/.zshrc
```

---

### 方法 3: 使用 nano 编辑器

```bash
# 1. 打开文件
nano ~/.zshrc

# 2. 在文件末尾添加以下内容:
# >>> nvm initialize >>>
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
# <<< nvm initialize <<<

# 3. 保存: Ctrl+O, Enter, Ctrl+X
```

---

## ✅ 验证修改

修改完成后，运行以下命令验证：

```bash
# 1. 重新加载配置
source ~/.zshrc

# 2. 检查 Node.js 版本
node --version    # 应该显示 v24.11.0

# 3. 检查 npm 版本
npm --version     # 应该显示 11.x.x

# 4. 检查 nvm
nvm --version
```

---

## 🚀 完成后的步骤

修改完成并验证后：

```bash
# 1. 重新启动 VSCode（完全关闭并重新打开）

# 2. 或者在新的终端中验证
node --version    # 应该显示 v24.11.0

# 3. 启动应用
./start-dev-nvm.sh
```

---

## 📝 完整的 ~/.zshrc 文件内容

如果您想完全替换 ~/.zshrc 文件，使用以下内容：

```bash
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/opt/anaconda3/bin/conda' 'shell.zsh' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/opt/anaconda3/etc/profile.d/conda.sh" ]; then
        . "/opt/anaconda3/etc/profile.d/conda.sh"
    else
        export PATH="/opt/anaconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

# >>> nvm initialize >>>
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
# <<< nvm initialize <<<
```

---

## 💡 关键点

1. **nvm 配置必须在 conda 配置之后** - 这样 nvm 的 Node.js 会优先于系统的 Node.js
2. **必须重新加载配置** - 修改后需要运行 `source ~/.zshrc` 或重启终端
3. **权限问题** - 如果文件由 root 拥有，VSCode 会提示需要 sudo 权限

---

## 🎯 下一步

1. ✅ 使用上述方法之一修改 ~/.zshrc
2. ✅ 验证修改: `source ~/.zshrc && node --version`
3. ✅ 重新启动 VSCode
4. ✅ 运行: `./start-dev-nvm.sh`

祝您使用愉快！🚀

