#!/bin/bash

# Node.js 升级脚本 - 安装到本地目录（无需 sudo）

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  Node.js 升级脚本 - 升级到 Node.js 18 LTS                    ║"
echo "║  安装到本地目录（无需 sudo）                                  ║"
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

# 创建本地 Node.js 目录
NODE_HOME="$HOME/.local/nodejs"
mkdir -p "$NODE_HOME"

echo "📥 下载 Node.js 18.20.4..."
echo "下载链接: $DOWNLOAD_URL"
echo "安装目录: $NODE_HOME"
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

# 安装到本地目录
echo "📝 安装到 $NODE_HOME..."

# 复制文件
cp -r "$EXTRACTED_DIR/bin" "$NODE_HOME/"
cp -r "$EXTRACTED_DIR/lib" "$NODE_HOME/"
cp -r "$EXTRACTED_DIR/include" "$NODE_HOME/"
cp -r "$EXTRACTED_DIR/share" "$NODE_HOME/"

echo "✅ 安装完成"
echo ""

# 清理临时文件
cd /
rm -rf "$TEMP_DIR"

# 验证安装
echo "📦 验证安装..."
echo ""
echo "Node.js 版本:"
"$NODE_HOME/bin/node" --version
echo ""
echo "npm 版本:"
"$NODE_HOME/bin/npm" --version
echo ""

# 检查版本
NODE_VERSION=$("$NODE_HOME/bin/node" --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -ge 18 ]; then
    echo "✅ Node.js 升级成功！"
    echo ""
    echo "新版本已安装到: $NODE_HOME"
    echo ""
    echo "现在需要配置 PATH 环境变量。请按照以下步骤操作:"
    echo ""
    echo "1️⃣  编辑您的 shell 配置文件:"
    echo "   nano ~/.zshrc  # 或 nano ~/.bashrc"
    echo ""
    echo "2️⃣  在文件末尾添加以下行:"
    echo "   export PATH=\"$NODE_HOME/bin:\$PATH\""
    echo ""
    echo "3️⃣  保存文件（Ctrl+O, Enter, Ctrl+X）"
    echo ""
    echo "4️⃣  重新加载配置:"
    echo "   source ~/.zshrc  # 或 source ~/.bashrc"
    echo ""
    echo "5️⃣  验证新版本:"
    echo "   node --version"
    echo ""
    echo "6️⃣  然后运行应用:"
    echo "   ./start-dev.sh"
    echo ""
else
    echo "❌ 升级失败，版本仍然过低"
    exit 1
fi

