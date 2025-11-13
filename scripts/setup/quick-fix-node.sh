#!/bin/bash

# 快速修复 Node.js 版本不一致问题

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                  🔧 Node.js 版本不一致 - 快速修复                         ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# ============================================================================
# 第一步: 检查 nvm
# ============================================================================

echo "📦 第一步: 检查 nvm..."
echo ""

NVM_DIR="$HOME/.nvm"

if [ ! -d "$NVM_DIR" ]; then
    echo "❌ 错误: nvm 未安装"
    echo ""
    echo "请先安装 nvm:"
    echo "  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
    exit 1
fi

if [ ! -s "$NVM_DIR/nvm.sh" ]; then
    echo "❌ 错误: nvm.sh 不存在"
    exit 1
fi

echo "✅ nvm 已安装"
echo ""

# ============================================================================
# 第二步: 加载 nvm
# ============================================================================

echo "📦 第二步: 加载 nvm..."
echo ""

source "$NVM_DIR/nvm.sh"

if ! command -v nvm &> /dev/null; then
    echo "❌ 错误: nvm 命令加载失败"
    exit 1
fi

echo "✅ nvm 已加载"
echo ""

# ============================================================================
# 第三步: 检查 Node.js 版本
# ============================================================================

echo "📦 第三步: 检查 Node.js 版本..."
echo ""

if ! command -v node &> /dev/null; then
    echo "❌ 错误: Node.js 未安装"
    echo ""
    echo "请使用 nvm 安装 Node.js:"
    echo "  nvm install 24"
    exit 1
fi

NODE_VERSION=$(node --version)
NODE_MAJOR=$(echo $NODE_VERSION | cut -d'v' -f2 | cut -d'.' -f1)

echo "当前 Node.js 版本: $NODE_VERSION"
echo ""

if [ "$NODE_MAJOR" -lt 18 ]; then
    echo "❌ Node.js 版本过低"
    echo ""
    echo "请使用 nvm 升级:"
    echo "  nvm install 24"
    echo "  nvm use 24"
    exit 1
fi

echo "✅ Node.js 版本满足要求"
echo ""

# ============================================================================
# 第四步: 修复 PATH
# ============================================================================

echo "📦 第四步: 修复 PATH..."
echo ""

# 确定 shell 配置文件
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
else
    SHELL_RC="$HOME/.bashrc"
fi

echo "使用 shell 配置文件: $SHELL_RC"
echo ""

# 检查是否已配置
if grep -q "export NVM_DIR" "$SHELL_RC"; then
    echo "✅ nvm 已在 $SHELL_RC 中配置"
else
    echo "⚠️  nvm 未在 $SHELL_RC 中配置"
    echo ""
    echo "添加 nvm 配置..."
    
    cat >> "$SHELL_RC" << 'EOF'

# nvm configuration (added by quick-fix-node.sh)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
EOF
    
    echo "✅ nvm 配置已添加"
fi

echo ""

# ============================================================================
# 第五步: 清除前端缓存
# ============================================================================

echo "📦 第五步: 清除前端缓存..."
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ -d "$SCRIPT_DIR/frontend" ]; then
    cd "$SCRIPT_DIR/frontend"
    
    if [ -d "node_modules" ]; then
        echo "删除 node_modules..."
        rm -rf node_modules
        echo "✅ node_modules 已删除"
    fi
    
    if [ -f "package-lock.json" ]; then
        echo "删除 package-lock.json..."
        rm -f package-lock.json
        echo "✅ package-lock.json 已删除"
    fi
    
    if [ -d ".vite" ]; then
        echo "删除 .vite..."
        rm -rf .vite
        echo "✅ .vite 已删除"
    fi
    
    if [ -d "dist" ]; then
        echo "删除 dist..."
        rm -rf dist
        echo "✅ dist 已删除"
    fi
    
    echo ""
    echo "重新安装前端依赖..."
    npm install
    echo "✅ 前端依赖已安装"
else
    echo "⚠️  frontend 目录不存在"
fi

echo ""

# ============================================================================
# 第六步: 完成
# ============================================================================

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║  ✅ 修复完成！                                                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

echo "📝 后续步骤:"
echo ""
echo "1️⃣  重新加载 shell 配置:"
echo "   source $SHELL_RC"
echo ""
echo "2️⃣  验证 Node.js 版本:"
echo "   node --version"
echo ""
echo "3️⃣  启动应用:"
echo "   ./start-dev-nvm.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

