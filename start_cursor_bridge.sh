#!/bin/bash

# Cursor Bridge 启动脚本

# 设置Python路径
export PYTHONPATH=$PWD/src:$PYTHONPATH

# 启动服务器
python3 -m cursor_bridge.cli start --config cursor_bridge_config.yaml
