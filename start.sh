#!/bin/bash

# CDRLApp 启动脚本
# 用法: ./start.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查环境
check_environment() {
    print_info "检查环境..."
    
    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js 未安装"
        exit 1
    fi
    NODE_VERSION=$(node --version)
    print_success "Node.js 已安装: $NODE_VERSION"
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装"
        exit 1
    fi
    PYTHON_VERSION=$(python3 --version)
    print_success "Python3 已安装: $PYTHON_VERSION"
    
    # 检查 npm
    if ! command -v npm &> /dev/null; then
        print_error "npm 未安装"
        exit 1
    fi
    NPM_VERSION=$(npm --version)
    print_success "npm 已安装: $NPM_VERSION"
}

# 启动后端
start_backend() {
    print_info "启动后端服务..."
    
    cd backend
    
    # 检查依赖
    if [ ! -d "venv" ]; then
        print_warning "虚拟环境不存在，创建虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 安装依赖
    if [ ! -f "requirements.txt" ]; then
        print_warning "requirements.txt 不存在"
    else
        pip install -q -r requirements.txt
    fi
    
    # 启动服务
    print_success "后端服务启动中..."
    python3 -m uvicorn app.main:app --reload --port 8000 &
    BACKEND_PID=$!
    
    cd ..
    
    # 等待后端启动
    sleep 2
    
    if kill -0 $BACKEND_PID 2>/dev/null; then
        print_success "后端服务已启动 (PID: $BACKEND_PID)"
        print_info "后端地址: http://localhost:8000"
    else
        print_error "后端服务启动失败"
        exit 1
    fi
}

# 启动前端
start_frontend() {
    print_info "启动前端服务..."
    
    cd frontend
    
    # 检查依赖
    if [ ! -d "node_modules" ]; then
        print_warning "node_modules 不存在，安装依赖..."
        npm install
    fi
    
    # 启动服务
    print_success "前端服务启动中..."
    npm run dev &
    FRONTEND_PID=$!
    
    cd ..
    
    # 等待前端启动
    sleep 3
    
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        print_success "前端服务已启动 (PID: $FRONTEND_PID)"
        print_info "前端地址: http://localhost:3001"
    else
        print_error "前端服务启动失败"
        exit 1
    fi
}

# 清理函数
cleanup() {
    print_warning "正在停止服务..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        print_success "后端服务已停止"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        print_success "前端服务已停止"
    fi
    
    print_info "程序已退出"
}

# 设置退出处理
trap cleanup EXIT INT TERM

# 主程序
main() {
    clear
    
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════╗"
    echo "║   CDRLApp - 启动程序                   ║"
    echo "║   Railway Construction Quality         ║"
    echo "║   Supervision Issue Database           ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}"
    
    print_info "开始启动应用..."
    echo ""
    
    # 检查环境
    check_environment
    echo ""
    
    # 启动后端
    start_backend
    echo ""
    
    # 启动前端
    start_frontend
    echo ""
    
    # 显示启动完成信息
    print_success "应用启动完成！"
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ 所有服务已启动${NC}"
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo ""
    echo -e "📱 前端应用: ${BLUE}http://localhost:3001${NC}"
    echo -e "🔌 后端 API: ${BLUE}http://localhost:8000${NC}"
    echo -e "📚 API 文档: ${BLUE}http://localhost:8000/docs${NC}"
    echo ""
    echo -e "${YELLOW}按 Ctrl+C 停止所有服务${NC}"
    echo ""
    
    # 保持脚本运行
    wait
}

# 运行主程序
main

