#!/bin/bash

# Node.js 升级脚本

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Node.js 升级脚本 - 升级到 Node.js 18 LTS                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# 检查当前 Node.js 版本
echo "📦 当前 Node.js 版本:"
node --version
npm --version
echo ""

# 获取系统信息
ARCH=$(uname -m)
OS=$(uname -s)

echo "系统信息:"
echo "  操作系统: $OS"
echo "  架构: $ARCH"
echo ""

# 确定下载链接
if [ "$OS" = "Darwin" ]; then
    if [ "$ARCH" = "arm64" ]; then
        # Apple Silicon (M1/M2/M3)
        DOWNLOAD_URL="https://nodejs.org/dist/v18.20.4/node-v18.20.4-darwin-arm64.tar.xz"
        FILENAME="node-v18.20.4-darwin-arm64.tar.xz"
    else
        # Intel Mac
        DOWNLOAD_URL="https://nodejs.org/dist/v18.20.4/node-v18.20.4-darwin-x64.tar.xz"
        FILENAME="node-v18.20.4-darwin-x64.tar.xz"
    fi
elif [ "$OS" = "Linux" ]; then
    if [ "$ARCH" = "x86_64" ]; then
        DOWNLOAD_URL="https://nodejs.org/dist/v18.20.4/node-v18.20.4-linux-x64.tar.xz"
        FILENAME="node-v18.20.4-linux-x64.tar.xz"
    else
        DOWNLOAD_URL="https://nodejs.org/dist/v18.20.4/node-v18.20.4-linux-arm64.tar.xz"
        FILENAME="node-v18.20.4-linux-arm64.tar.xz"
    fi
else
    echo "❌ 不支持的操作系统: $OS"
    exit 1
fi

echo "📥 下载 Node.js 18.20.4..."
echo "下载链接: $DOWNLOAD_URL"
echo ""

# 创建临时目录
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# 下载 Node.js
if ! curl -L -o "$FILENAME" "$DOWNLOAD_URL"; then
    echo "❌ 下载失败"
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo "✅ 下载完成"
echo ""

# 解压
echo "📦 解压文件..."
if ! tar -xf "$FILENAME"; then
    echo "❌ 解压失败"
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo "✅ 解压完成"
echo ""

# 获取解压后的目录名
EXTRACTED_DIR=$(ls -d node-* | head -1)

# 安装到 /usr/local
echo "📝 安装到 /usr/local..."
echo "需要输入密码来完成安装"
echo ""

# 备份旧版本
if [ -d "/usr/local/bin/node" ]; then
    echo "备份旧版本..."
    sudo mv /usr/local/bin/node /usr/local/bin/node.old || true
    sudo mv /usr/local/bin/npm /usr/local/bin/npm.old || true
    sudo mv /usr/local/bin/npx /usr/local/bin/npx.old || true
fi

# 复制新版本
sudo cp -r "$EXTRACTED_DIR/bin/node" /usr/local/bin/
sudo cp -r "$EXTRACTED_DIR/bin/npm" /usr/local/bin/
sudo cp -r "$EXTRACTED_DIR/bin/npx" /usr/local/bin/

# 复制 lib 文件
sudo cp -r "$EXTRACTED_DIR/lib/node_modules" /usr/local/lib/

echo "✅ 安装完成"
echo ""

# 清理临时文件
cd /
rm -rf "$TEMP_DIR"

# 验证安装
echo "📦 验证安装..."
echo ""
echo "Node.js 版本:"
/usr/local/bin/node --version
echo ""
echo "npm 版本:"
/usr/local/bin/npm --version
echo ""

# 检查版本
NODE_VERSION=$(/usr/local/bin/node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -ge 18 ]; then
    echo "✅ Node.js 升级成功！"
    echo ""
    echo "新版本已安装到: /usr/local/bin/"
    echo ""
    echo "请重新启动终端或运行以下命令来使用新版本:"
    echo "  source ~/.zshrc  # 或 ~/.bashrc"
    echo ""
    echo "然后运行:"
    echo "  ./start-dev.sh"
else
    echo "❌ 升级失败，版本仍然过低"
    exit 1
fi

