#!/bin/bash

# Cursor Bridge 安装脚本
# 企业远程开发解决方案

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python版本
check_python() {
    log_info "检查Python版本..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装，请先安装Python 3.9或更高版本"
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    required_version="3.9"
    
    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
        log_error "Python版本过低，需要Python 3.9或更高版本，当前版本: $python_version"
        exit 1
    fi
    
    log_success "Python版本检查通过: $python_version"
}

# 检查pip
check_pip() {
    log_info "检查pip..."
    
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 未安装，请先安装pip"
        exit 1
    fi
    
    log_success "pip检查通过"
}

# 安装依赖
install_dependencies() {
    log_info "安装Python依赖包..."
    
    # 升级pip
    log_info "升级pip..."
    python3 -m pip install --upgrade pip
    
    # 安装依赖
    log_info "安装项目依赖..."
    pip3 install -r requirements.txt
    
    log_success "依赖安装完成"
}

# 创建配置文件
setup_config() {
    log_info "设置配置文件..."
    
    if [ ! -f "cursor_bridge_config.yaml" ]; then
        log_info "生成默认配置文件..."
        export PYTHONPATH=$PWD/src:$PYTHONPATH
        python3 -m cursor_bridge.cli init-config
        log_success "配置文件已生成: cursor_bridge_config.yaml"
    else
        log_warning "配置文件已存在，跳过生成"
    fi
}

# 运行测试
run_tests() {
    log_info "运行基本测试..."
    
    export PYTHONPATH=$PWD/src:$PYTHONPATH
    
    # 测试版本
    log_info "测试版本信息..."
    python3 -m cursor_bridge.cli version
    
    # 测试ping
    log_info "测试ping功能..."
    python3 -m cursor_bridge.cli ping
    
    # 测试健康检查
    log_info "测试健康检查..."
    python3 -m cursor_bridge.cli health
    
    log_success "基本测试通过"
}

# 创建启动脚本
create_start_script() {
    log_info "创建启动脚本..."
    
    cat > start_cursor_bridge.sh << 'EOF'
#!/bin/bash

# Cursor Bridge 启动脚本

# 设置Python路径
export PYTHONPATH=$PWD/src:$PYTHONPATH

# 启动服务器
python3 -m cursor_bridge.cli start --config cursor_bridge_config.yaml
EOF

    chmod +x start_cursor_bridge.sh
    log_success "启动脚本已创建: start_cursor_bridge.sh"
}

# 生成Cursor MCP配置
create_cursor_config() {
    log_info "生成Cursor MCP配置..."
    
    current_dir=$(pwd)
    
    cat > cursor_mcp_config.json << EOF
{
  "mcpServers": {
    "cursor-bridge": {
      "command": "python3",
      "args": [
        "-m", 
        "cursor_bridge.cli", 
        "mcp", 
        "--config", 
        "${current_dir}/cursor_bridge_config.yaml"
      ],
      "env": {
        "PYTHONPATH": "${current_dir}/src"
      }
    }
  }
}
EOF

    log_success "Cursor MCP配置已生成: cursor_mcp_config.json"
}

# 显示使用说明
show_usage() {
    log_success "🎉 Cursor Bridge 安装完成！"
    echo ""
    echo "📋 使用说明:"
    echo "  1. 编辑配置文件: cursor_bridge_config.yaml"
    echo "  2. 启动服务器: ./start_cursor_bridge.sh"
    echo "  3. 或手动启动: PYTHONPATH=\$PWD/src python3 -m cursor_bridge.cli start"
    echo ""
    echo "🔗 Cursor IDE 集成:"
    echo "  1. 打开 Cursor IDE 设置"
    echo "  2. 找到 'MCP Servers' 配置"
    echo "  3. 复制 cursor_mcp_config.json 的内容到配置中"
    echo "  4. 重启 Cursor IDE"
    echo "  5. 在 Cursor 中就可以使用 cursor-bridge 工具了！"
    echo ""
    echo "🔧 配置说明:"
    echo "  - 配置文件包含服务器连接信息"
    echo "  - 支持直接SSH连接和企业代理连接"
    echo "  - 详细配置请参考 README.md"
    echo ""
    echo "🧪 测试MCP服务器:"
    echo "  - 测试MCP: PYTHONPATH=\$PWD/src python3 -m cursor_bridge.cli mcp"
    echo ""
    echo "📚 更多帮助:"
    echo "  - 查看帮助: PYTHONPATH=\$PWD/src python3 -m cursor_bridge.cli --help"
    echo "  - 项目文档: https://github.com/maricoxu/cursor-bridge"
}

# 主安装流程
main() {
    echo "🚀 开始安装 Cursor Bridge..."
    echo ""
    
    # 检查环境
    check_python
    check_pip
    
    # 安装依赖
    install_dependencies
    
    # 设置配置
    setup_config
    
    # 运行测试
    run_tests
    
    # 创建启动脚本
    create_start_script
    
    # 生成Cursor配置
    create_cursor_config
    
    # 显示使用说明
    show_usage
}

# 错误处理
trap 'log_error "安装过程中发生错误，请检查上面的错误信息"; exit 1' ERR

# 运行主函数
main "$@" 