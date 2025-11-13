#!/bin/bash

# 快速 Node.js 升级脚本 - 一键升级到 Node.js 18

set -e  # 遇到错误立即退出

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  🚀 Node.js 快速升级脚本                                      ║"
echo "║  升级到 Node.js 18.20.4                                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# 检查当前版本
echo "📦 当前版本:"
echo "  Node.js: $(node --version)"
echo "  npm: $(npm --version)"
echo ""

# 获取系统信息
ARCH=$(uname -m)
OS=$(uname -s)

if [ "$OS" != "Darwin" ]; then
    echo "❌ 此脚本仅支持 macOS"
    exit 1
fi

# 确定下载链接
if [ "$ARCH" = "arm64" ]; then
    DOWNLOAD_URL="https://nodejs.org/dist/v18.20.4/node-v18.20.4-darwin-arm64.tar.xz"
    FILENAME="node-v18.20.4-darwin-arm64.tar.xz"
    echo "✅ 检测到 Apple Silicon (M1/M2/M3)"
else
    DOWNLOAD_URL="https://nodejs.org/dist/v18.20.4/node-v18.20.4-darwin-x64.tar.xz"
    FILENAME="node-v18.20.4-darwin-x64.tar.xz"
    echo "✅ 检测到 Intel Mac"
fi
echo ""

# 创建安装目录
NODE_HOME="$HOME/.local/nodejs"
mkdir -p "$NODE_HOME"

echo "📥 下载 Node.js 18.20.4..."
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

if ! curl -L -o "$FILENAME" "$DOWNLOAD_URL"; then
    echo "❌ 下载失败"
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo "✅ 下载完成"
echo ""

echo "📦 解压文件..."
if ! tar -xf "$FILENAME"; then
    echo "❌ 解压失败"
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo "✅ 解压完成"
echo ""

EXTRACTED_DIR=$(ls -d node-* | head -1)

echo "📝 安装到 $NODE_HOME..."
cp -r "$EXTRACTED_DIR/bin" "$NODE_HOME/"
cp -r "$EXTRACTED_DIR/lib" "$NODE_HOME/"
cp -r "$EXTRACTED_DIR/include" "$NODE_HOME/"
cp -r "$EXTRACTED_DIR/share" "$NODE_HOME/"

echo "✅ 安装完成"
echo ""

cd /
rm -rf "$TEMP_DIR"

# 验证安装
echo "📦 验证安装..."
NEW_NODE_VERSION=$("$NODE_HOME/bin/node" --version)
NEW_NPM_VERSION=$("$NODE_HOME/bin/npm" --version)

echo "  Node.js: $NEW_NODE_VERSION"
echo "  npm: $NEW_NPM_VERSION"
echo ""

# 配置 PATH
echo "⚙️  配置 PATH..."

SHELL_RC="$HOME/.zshrc"
if [ ! -f "$SHELL_RC" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

# 检查是否已经配置
if grep -q "\.local/nodejs/bin" "$SHELL_RC"; then
    echo "✅ PATH 已配置"
else
    echo "添加 PATH 配置到 $SHELL_RC"
    echo "" >> "$SHELL_RC"
    echo "# Node.js 18 (added by quick-upgrade-nodejs.sh)" >> "$SHELL_RC"
    echo "export PATH=\"\$HOME/.local/nodejs/bin:\$PATH\"" >> "$SHELL_RC"
    echo "✅ PATH 配置完成"
fi
echo ""

# 提示用户
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  ✅ Node.js 升级完成！                                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📝 后续步骤:"
echo ""
echo "1️⃣  重新加载 shell 配置:"
echo "   source ~/.zshrc  # 或 source ~/.bashrc"
echo ""
echo "2️⃣  验证新版本:"
echo "   node --version"
echo ""
echo "3️⃣  清除前端缓存:"
echo "   cd frontend"
echo "   rm -rf node_modules package-lock.json"
echo "   npm install"
echo ""
echo "4️⃣  启动应用:"
echo "   cd .."
echo "   ./start-dev.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 提示: 如果升级后仍显示旧版本，请重新启动 VSCode"
echo ""

