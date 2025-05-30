#!/bin/bash
# Cursor Bridge 启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

echo "🚀 启动 Cursor Bridge MCP 服务器..."
python3 -m cursor_bridge.cli --config "$SCRIPT_DIR/cursor_bridge_config.yaml" mcp
