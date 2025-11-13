#!/bin/bash

# Node.js 环境诊断脚本

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    🔍 Node.js 环境诊断脚本                                ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# ============================================================================
# 1. 检查 nvm 状态
# ============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  nvm 状态检查"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NVM_DIR="$HOME/.nvm"

if [ -d "$NVM_DIR" ]; then
    echo "✅ nvm 目录存在: $NVM_DIR"
    
    if [ -s "$NVM_DIR/nvm.sh" ]; then
        echo "✅ nvm.sh 脚本存在"
        
        # 加载 nvm
        source "$NVM_DIR/nvm.sh"
        
        # 检查 nvm 命令
        if command -v nvm &> /dev/null; then
            echo "✅ nvm 命令可用"
            echo ""
            echo "已安装的 Node.js 版本:"
            nvm list
        else
            echo "⚠️  nvm 命令不可用（可能需要重新加载 shell）"
        fi
    else
        echo "❌ nvm.sh 脚本不存在"
    fi
else
    echo "❌ nvm 未安装"
fi

echo ""

# ============================================================================
# 2. 检查 Node.js 版本
# ============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  Node.js 版本检查"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if command -v node &> /dev/null; then
    NODE_PATH=$(which node)
    NODE_VERSION=$(node --version)
    echo "✅ node 命令可用"
    echo "   位置: $NODE_PATH"
    echo "   版本: $NODE_VERSION"
else
    echo "❌ node 命令不可用"
fi

echo ""

if command -v npm &> /dev/null; then
    NPM_PATH=$(which npm)
    NPM_VERSION=$(npm --version)
    echo "✅ npm 命令可用"
    echo "   位置: $NPM_PATH"
    echo "   版本: $NPM_VERSION"
else
    echo "❌ npm 命令不可用"
fi

echo ""

# ============================================================================
# 3. 检查 PATH 环境变量
# ============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  PATH 环境变量检查"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "当前 PATH:"
echo "$PATH" | tr ':' '\n' | nl
echo ""

# 检查 nvm 相关的路径
if echo "$PATH" | grep -q "\.nvm"; then
    echo "✅ PATH 中包含 nvm 相关路径"
else
    echo "⚠️  PATH 中不包含 nvm 相关路径"
fi

echo ""

# ============================================================================
# 4. 检查 shell 配置文件
# ============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  Shell 配置文件检查"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

SHELL_NAME=$(basename $SHELL)
echo "当前 Shell: $SHELL_NAME"
echo ""

# 检查 .bashrc
if [ -f "$HOME/.bashrc" ]; then
    echo "✅ ~/.bashrc 存在"
    if grep -q "nvm" "$HOME/.bashrc"; then
        echo "   ✅ 包含 nvm 配置"
    else
        echo "   ⚠️  不包含 nvm 配置"
    fi
else
    echo "❌ ~/.bashrc 不存在"
fi

# 检查 .zshrc
if [ -f "$HOME/.zshrc" ]; then
    echo "✅ ~/.zshrc 存在"
    if grep -q "nvm" "$HOME/.zshrc"; then
        echo "   ✅ 包含 nvm 配置"
    else
        echo "   ⚠️  不包含 nvm 配置"
    fi
else
    echo "❌ ~/.zshrc 不存在"
fi

echo ""

# ============================================================================
# 5. 检查旧版本 Node.js
# ============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  旧版本 Node.js 检查"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 检查常见的 Node.js 安装位置
COMMON_PATHS=(
    "/usr/local/bin/node"
    "/usr/bin/node"
    "/opt/homebrew/bin/node"
    "$HOME/.local/nodejs/bin/node"
)

for path in "${COMMON_PATHS[@]}"; do
    if [ -f "$path" ]; then
        version=$("$path" --version)
        echo "⚠️  发现旧版本: $path ($version)"
    fi
done

echo ""

# ============================================================================
# 6. 建议
# ============================================================================

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 建议"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

NODE_VERSION=$(node --version 2>/dev/null | cut -d'v' -f2 | cut -d'.' -f1)

if [ -z "$NODE_VERSION" ]; then
    echo "❌ 无法检测到 Node.js 版本"
    echo ""
    echo "请按照以下步骤操作:"
    echo "1. 重新启动 VSCode"
    echo "2. 打开新的终端窗口"
    echo "3. 运行: nvm use 24"
    echo "4. 验证: node --version"
elif [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js 版本过低 (v$NODE_VERSION)"
    echo ""
    echo "请使用 nvm 升级:"
    echo "1. nvm install 24"
    echo "2. nvm use 24"
    echo "3. nvm alias default 24"
    echo "4. 重新启动终端"
else
    echo "✅ Node.js 版本满足要求 (v$NODE_VERSION)"
    echo ""
    echo "您可以使用以下脚本启动应用:"
    echo "1. ./start-dev-nvm.sh  (推荐，专为 nvm 用户设计)"
    echo "2. ./start-dev.sh      (通用脚本)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

