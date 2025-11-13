#!/bin/bash

# 快速修复脚本 - 解决常见问题

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  CDRL 项目 - 快速修复脚本                                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 菜单
show_menu() {
    echo "请选择要执行的操作:"
    echo ""
    echo "1. 清除所有缓存并重新安装依赖"
    echo "2. 只清除后端缓存"
    echo "3. 只清除前端缓存"
    echo "4. 检查 Node.js 版本"
    echo "5. 检查 Python 版本"
    echo "6. 查看后端日志"
    echo "7. 杀死所有 Node.js 进程"
    echo "8. 杀死所有 Python 进程"
    echo "9. 重置整个项目"
    echo "0. 退出"
    echo ""
    read -p "请输入选项 (0-9): " choice
}

# 清除所有缓存
clean_all() {
    echo -e "${BLUE}🧹 清除所有缓存...${NC}"
    
    # 清除后端缓存
    echo "清除后端缓存..."
    cd "$SCRIPT_DIR/backend"
    rm -rf venv __pycache__ .pytest_cache *.pyc
    pip cache purge 2>/dev/null || true
    
    # 清除前端缓存
    echo "清除前端缓存..."
    cd "$SCRIPT_DIR/frontend"
    rm -rf node_modules package-lock.json dist .vite
    npm cache clean --force 2>/dev/null || true
    
    echo -e "${GREEN}✅ 缓存清除完成${NC}"
    echo ""
}

# 清除后端缓存
clean_backend() {
    echo -e "${BLUE}🧹 清除后端缓存...${NC}"
    cd "$SCRIPT_DIR/backend"
    rm -rf venv __pycache__ .pytest_cache *.pyc
    pip cache purge 2>/dev/null || true
    echo -e "${GREEN}✅ 后端缓存清除完成${NC}"
    echo ""
}

# 清除前端缓存
clean_frontend() {
    echo -e "${BLUE}🧹 清除前端缓存...${NC}"
    cd "$SCRIPT_DIR/frontend"
    rm -rf node_modules package-lock.json dist .vite
    npm cache clean --force 2>/dev/null || true
    echo -e "${GREEN}✅ 前端缓存清除完成${NC}"
    echo ""
}

# 检查 Node.js 版本
check_node() {
    echo -e "${BLUE}📦 检查 Node.js 版本...${NC}"
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d'v' -f2 | cut -d'.' -f1)
        echo "Node.js 版本: $NODE_VERSION"
        
        if [ "$NODE_MAJOR" -lt 18 ]; then
            echo -e "${RED}❌ Node.js 版本过低，需要 18.0.0 或更高${NC}"
            echo "建议升级:"
            echo "  使用 nvm: nvm install 18"
            echo "  或访问: https://nodejs.org/"
        else
            echo -e "${GREEN}✅ Node.js 版本满足要求${NC}"
        fi
    else
        echo -e "${RED}❌ 未找到 Node.js${NC}"
    fi
    echo ""
}

# 检查 Python 版本
check_python() {
    echo -e "${BLUE}📦 检查 Python 版本...${NC}"
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        echo "$PYTHON_VERSION"
        echo -e "${GREEN}✅ Python 已安装${NC}"
    else
        echo -e "${RED}❌ 未找到 Python 3${NC}"
    fi
    echo ""
}

# 查看后端日志
view_backend_log() {
    echo -e "${BLUE}📋 后端日志:${NC}"
    if [ -f "/tmp/backend.log" ]; then
        tail -20 /tmp/backend.log
    else
        echo "未找到后端日志文件"
    fi
    echo ""
}

# 杀死所有 Node.js 进程
kill_node() {
    echo -e "${YELLOW}⚠️  杀死所有 Node.js 进程...${NC}"
    pkill -f "node" || true
    pkill -f "npm" || true
    echo -e "${GREEN}✅ 完成${NC}"
    echo ""
}

# 杀死所有 Python 进程
kill_python() {
    echo -e "${YELLOW}⚠️  杀死所有 Python 进程...${NC}"
    pkill -f "python" || true
    pkill -f "uvicorn" || true
    echo -e "${GREEN}✅ 完成${NC}"
    echo ""
}

# 重置整个项目
reset_project() {
    echo -e "${RED}⚠️  警告: 这将删除所有缓存和依赖${NC}"
    read -p "确定要继续吗? (y/n): " confirm
    
    if [ "$confirm" = "y" ]; then
        echo -e "${BLUE}🔄 重置项目...${NC}"
        
        # 杀死所有进程
        pkill -f "node" || true
        pkill -f "npm" || true
        pkill -f "python" || true
        pkill -f "uvicorn" || true
        
        # 清除所有缓存
        clean_all
        
        echo -e "${GREEN}✅ 项目重置完成${NC}"
        echo "现在可以运行: ./start-dev.sh"
    else
        echo "已取消"
    fi
    echo ""
}

# 主循环
while true; do
    show_menu
    
    case $choice in
        1)
            clean_all
            ;;
        2)
            clean_backend
            ;;
        3)
            clean_frontend
            ;;
        4)
            check_node
            ;;
        5)
            check_python
            ;;
        6)
            view_backend_log
            ;;
        7)
            kill_node
            ;;
        8)
            kill_python
            ;;
        9)
            reset_project
            ;;
        0)
            echo "退出"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ 无效的选项${NC}"
            echo ""
            ;;
    esac
done

