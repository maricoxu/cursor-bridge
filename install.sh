#!/bin/bash

# Cursor Bridge 安装脚本
# 基于本地tmux会话的远程命令执行

set -e

echo "🚀 开始安装 Cursor Bridge (tmux版本)..."

# 检查Python版本
echo "📋 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到python3，请先安装Python 3.9+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ 找到Python $PYTHON_VERSION"

# 检查tmux
echo "📋 检查tmux..."
if ! command -v tmux &> /dev/null; then
    echo "❌ 错误: 未找到tmux，请先安装tmux"
    echo "   macOS: brew install tmux"
    echo "   Ubuntu: sudo apt install tmux"
    exit 1
fi
echo "✅ 找到tmux $(tmux -V)"

# 安装Python依赖
echo "📦 安装Python依赖..."
pip3 install --user -r requirements.txt

# 设置环境变量
echo "🔧 设置环境..."
export PYTHONPATH="$PWD/src:$PYTHONPATH"

# 检查配置文件
if [ ! -f "cursor_bridge_config.local.yaml" ]; then
    echo "⚠️  未找到本地配置文件，使用默认配置"
    echo "   配置文件: cursor_bridge_config.local.yaml"
else
    echo "✅ 找到本地配置文件"
fi

# 生成Cursor MCP配置
echo "📝 生成Cursor MCP配置..."
CURRENT_DIR=$(pwd)
cat > cursor_mcp_config.json << EOF
{
  "mcpServers": {
    "cursor-bridge": {
      "command": "python3",
      "args": [
        "-m", 
        "cursor_bridge.cli", 
        "--config", 
        "$CURRENT_DIR/cursor_bridge_config.local.yaml",
        "mcp"
      ],
      "env": {
        "PYTHONPATH": "$CURRENT_DIR/src"
      }
    }
  }
}
EOF

echo "✅ 生成了 cursor_mcp_config.json"

# 创建启动脚本
echo "📝 创建启动脚本..."
cat > start_cursor_bridge.sh << 'EOF'
#!/bin/bash
# Cursor Bridge 启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

echo "🚀 启动 Cursor Bridge MCP 服务器..."
echo "📁 配置文件: $SCRIPT_DIR/cursor_bridge_config.local.yaml"
echo "🔧 Python路径: $PYTHONPATH"

python3 -m cursor_bridge.cli --config "$SCRIPT_DIR/cursor_bridge_config.local.yaml" mcp
EOF

chmod +x start_cursor_bridge.sh
echo "✅ 创建了启动脚本 start_cursor_bridge.sh"

# 测试基本功能
echo "🧪 测试基本功能..."
if python3 -c "import sys; sys.path.insert(0, 'src'); from cursor_bridge.cli import cli; print('✅ 模块导入成功')"; then
    echo "✅ 基本功能测试通过"
else
    echo "❌ 基本功能测试失败，请检查依赖安装"
    exit 1
fi

echo ""
echo "🎉 安装完成！"
echo ""
echo "📋 下一步操作："
echo "1. 🔧 创建你的tmux会话并连接到远程服务器："
echo "   tmux new-session -d -s baidu-server"
echo "   tmux send-keys -t baidu-server 'ssh user@your-server' Enter"
echo ""
echo "2. 📝 编辑配置文件 cursor_bridge_config.local.yaml："
echo "   - 修改tmux会话名称"
echo "   - 设置工作目录"
echo ""
echo "3. 🎯 将 cursor_mcp_config.json 的内容添加到Cursor的MCP设置中"
echo ""
echo "4. 🔄 重启Cursor IDE"
echo ""
echo "🔧 测试命令："
echo "   export PYTHONPATH=$PWD/src:\$PYTHONPATH"
echo "   python3 -m cursor_bridge.cli --config cursor_bridge_config.local.yaml config"
echo ""
echo "📖 详细说明请参考 README.md"