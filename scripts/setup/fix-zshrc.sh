#!/bin/bash

# 修复 ~/.zshrc 以加载 nvm

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║                    🔧 修复 ~/.zshrc 以加载 nvm                           ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

ZSHRC="$HOME/.zshrc"

# 备份原文件
if [ -f "$ZSHRC" ]; then
    echo "📦 备份原文件..."
    cp "$ZSHRC" "$ZSHRC.backup.$(date +%s)"
    echo "✅ 备份完成"
    echo ""
fi

# 检查是否已经有 nvm 配置
if grep -q "nvm initialize" "$ZSHRC"; then
    echo "✅ ~/.zshrc 中已经有 nvm 配置"
    echo ""
else
    echo "📝 添加 nvm 配置到 ~/.zshrc..."
    echo "" >> "$ZSHRC"
    echo "# >>> nvm initialize >>>" >> "$ZSHRC"
    echo "export NVM_DIR=\"\$HOME/.nvm\"" >> "$ZSHRC"
    echo "[ -s \"\$NVM_DIR/nvm.sh\" ] && \\. \"\$NVM_DIR/nvm.sh\"  # This loads nvm" >> "$ZSHRC"
    echo "[ -s \"\$NVM_DIR/bash_completion\" ] && \\. \"\$NVM_DIR/bash_completion\"  # This loads nvm bash_completion" >> "$ZSHRC"
    echo "# <<< nvm initialize <<<" >> "$ZSHRC"
    echo "✅ nvm 配置已添加"
    echo ""
fi

# 验证配置
echo "📦 验证配置..."
echo ""
echo "~/.zshrc 中的 nvm 配置:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
grep -A 5 "nvm initialize" "$ZSHRC"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║  ✅ 修复完成！                                                            ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

echo "📝 后续步骤:"
echo ""
echo "1️⃣  重新启动 VSCode（完全关闭并重新打开）"
echo ""
echo "2️⃣  或者在终端中重新加载配置:"
echo "   source ~/.zshrc"
echo ""
echo "3️⃣  验证 Node.js 版本:"
echo "   node --version    # 应该显示 v24.11.0"
echo ""
echo "4️⃣  启动应用:"
echo "   ./start-dev-nvm.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

