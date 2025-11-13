#!/bin/bash

# 铁路工程质量安全监督问题库管理平台 - 开发启动脚本

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  铁路工程质量安全监督问题库管理平台 - 开发启动脚本            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 加载 nvm 环境（如果已安装）
export NVM_DIR="$HOME/.nvm"
if [ -s "$NVM_DIR/nvm.sh" ]; then
    source "$NVM_DIR/nvm.sh"
    echo "✅ nvm 已加载"
fi

# 加载 bash/zsh 配置文件中的环境变量
if [ -f "$HOME/.bashrc" ]; then
    source "$HOME/.bashrc"
fi
if [ -f "$HOME/.zshrc" ]; then
    source "$HOME/.zshrc"
fi

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python 3"
    echo "请先安装 Python 3.8 或更高版本"
    exit 1
fi

# 检查 Node.js 是否安装
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未找到 Node.js"
    echo "请先安装 Node.js 18.0.0 或更高版本"
    exit 1
fi

# 检查 Node.js 版本
NODE_VERSION=$(node --version | cut -d'v' -f2)
NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)

echo "✅ Python 版本: $(python3 --version)"
echo "✅ Node.js 版本: $(node --version)"
echo "✅ npm 版本: $(npm --version)"

if [ "$NODE_MAJOR" -lt 18 ]; then
    echo ""
    echo "⚠️  警告: Node.js 版本过低 (v$NODE_VERSION)"
    echo "⚠️  Vite 需要 Node.js 18.0.0 或更高版本"
    echo "⚠️  前端可能无法正常运行"
    echo ""
    echo "建议升级 Node.js:"
    echo "  使用 nvm: nvm install 18"
    echo "  或访问: https://nodejs.org/"
    echo ""
fi
echo ""

# 启动后端服务
echo "🚀 启动后端服务..."
echo "   后端服务将在 http://localhost:8000 启动"
echo ""

cd "$SCRIPT_DIR/backend"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📦 安装后端依赖..."
if ! pip install -q -r requirements.txt; then
    echo "❌ 后端依赖安装失败"
    echo "请检查 requirements.txt 中的依赖版本"
    exit 1
fi

# 启动后端服务（后台运行）
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"
echo ""

# 等待后端服务启动
sleep 3

# 启动前端开发服务器
echo "🚀 启动前端开发服务器..."
echo "   前端应用将在 http://localhost:3000 启动"
echo ""

cd "$SCRIPT_DIR/frontend"

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install --legacy-peer-deps
fi

# 启动前端开发服务器
npm run dev &
FRONTEND_PID=$!
echo "✅ 前端开发服务器已启动 (PID: $FRONTEND_PID)"
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  ✅ 应用已启动！                                              ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║  后端 API:     http://localhost:8000                          ║"
echo "║  后端文档:     http://localhost:8000/docs                     ║"
echo "║  前端应用:     http://localhost:3000                          ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║  按 Ctrl+C 停止所有服务                                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# 等待用户中断
wait

