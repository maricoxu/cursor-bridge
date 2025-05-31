#!/bin/bash

# Cursor Bridge 安装验证脚本

set -e

echo "🔍 验证 Cursor Bridge 安装..."

# 检查基本环境
echo "📋 检查环境..."

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装"
    exit 1
fi
echo "✅ Python3: $(python3 --version)"

# 检查tmux
if ! command -v tmux &> /dev/null; then
    echo "❌ tmux 未安装"
    exit 1
fi
echo "✅ tmux: $(tmux -V)"

# 检查配置文件
if [ ! -f "cursor_bridge_config.yaml" ]; then
    echo "❌ 配置文件 cursor_bridge_config.yaml 不存在"
    exit 1
fi
echo "✅ 配置文件存在"

# 检查源代码
if [ ! -d "src/cursor_bridge" ]; then
    echo "❌ 源代码目录不存在"
    exit 1
fi
echo "✅ 源代码目录存在"

# 设置环境变量
export PYTHONPATH="$PWD/src:$PYTHONPATH"

# 测试基本功能
echo "🧪 测试基本功能..."
if python3 -m cursor_bridge.cli version; then
    echo "✅ 基本功能正常"
else
    echo "❌ 基本功能测试失败"
    exit 1
fi

# 检查tmux会话
echo "🔍 检查tmux会话..."
if tmux list-sessions | grep -q "baidu-session"; then
    echo "✅ 找到 baidu-session"
else
    echo "⚠️  未找到 baidu-session，创建测试会话..."
    tmux new-session -d -s baidu-session
    echo "✅ 创建了测试会话"
fi

# 测试MCP服务器
echo "🧪 测试MCP服务器..."
echo '{"jsonrpc": "2.0", "method": "initialize", "id": 1, "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}' | python3 -m cursor_bridge.cli --config cursor_bridge_config.yaml mcp > /tmp/mcp_test.json

if grep -q '"result"' /tmp/mcp_test.json; then
    echo "✅ MCP服务器响应正常"
else
    echo "❌ MCP服务器测试失败"
    cat /tmp/mcp_test.json
    exit 1
fi

# 测试命令执行
echo "🧪 测试命令执行..."
echo '{"jsonrpc": "2.0", "method": "tools/call", "id": 2, "params": {"name": "execute_command", "arguments": {"command": "echo hello", "server": "baidu-server"}}}' | python3 -m cursor_bridge.cli --config cursor_bridge_config.yaml mcp > /tmp/cmd_test.json

if grep -q '"result"' /tmp/cmd_test.json && grep -q 'hello' /tmp/cmd_test.json; then
    echo "✅ 命令执行正常"
else
    echo "❌ 命令执行测试失败"
    cat /tmp/cmd_test.json
    exit 1
fi

# 清理临时文件
rm -f /tmp/mcp_test.json /tmp/cmd_test.json

echo ""
echo "🎉 所有测试通过！"
echo ""
echo "📋 下一步："
echo "1. 将 cursor_mcp_config.json 的内容添加到Cursor的MCP设置中"
echo "2. 重启Cursor IDE"
echo "3. 在Cursor中测试远程命令执行"
echo ""
echo "📖 详细设置指南请查看 CURSOR_SETUP.md" 