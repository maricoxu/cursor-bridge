# Cursor Bridge

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub repo](https://img.shields.io/badge/GitHub-cursor--bridge-blue.svg)](https://github.com/maricoxu/cursor-bridge)

🚀 **无缝远程开发桥梁** - 为Cursor IDE提供企业级远程终端访问解决方案

## 项目简介

Cursor Bridge 是一个基于Model Context Protocol (MCP)的远程终端代理系统，通过**本地tmux会话管理**的方式，让Cursor的AI Agent能够在已建立的远程连接中执行命令。

### 🎯 核心思路

利用**本地tmux会话**作为桥梁，这些会话内部已经通过企业VPN工具或跳板机连接到远程服务器：

```
你的指令 → Cursor Agent → cursor-bridge → 本地tmux会话 → relay-cli → 远程服务器
                                            ↑
                                    你手动建立的连接
```

### ✨ 核心特性

- 🔄 **复用现有连接**: 基于你已手动建立的tmux会话，无需重新认证
- 🎯 **零配置网络**: 不处理复杂的网络连接，专注于命令执行
- 🛡️ **安全可靠**: 基于现有安全架构，不改变网络拓扑
- ⚡ **即时响应**: 通过tmux命令实现毫秒级的指令发送和输出捕获
- 🔧 **简单部署**: 只需配置tmux会话名称即可使用
- 📊 **完整日志**: 所有命令执行都有详细记录

## 快速开始

### 前提条件

1. **已建立的远程连接**: 你需要在本地tmux会话中已经连接到远程服务器
2. **Python 3.9+**: 确保系统安装了Python 3.9或更高版本
3. **tmux**: 确保系统安装了tmux

### 步骤1：建立远程连接

首先，手动创建tmux会话并连接到远程服务器：

```bash
# 创建tmux会话
tmux new-session -d -s baidu-session

# 在会话中连接到远程服务器（使用你的连接方式）
tmux send-keys -t baidu-session "relay-cli connect your-server" Enter
# 或者使用SSH
# tmux send-keys -t baidu-session "ssh user@remote-server" Enter

# 验证连接成功
tmux attach -t baidu-session
# 确认你已经在远程服务器上，然后按 Ctrl+B, D 分离会话
```

### 步骤2：安装cursor-bridge

```bash
# 克隆项目
git clone https://github.com/maricoxu/cursor-bridge.git
cd cursor-bridge

# 安装依赖
pip3 install -r requirements.txt
```

### 步骤3：配置服务器

编辑 `cursor_bridge_config.yaml` 文件：

```yaml
servers:
  baidu-server:
    type: local_tmux
    tmux:
      session_name: "baidu-session"  # 你的tmux会话名称
      window_name: "relay-cli"       # 窗口名称（通常是0或main）
    session:
      name: "baidu-session"
      working_directory: "/workspace"  # 远程服务器的工作目录
      environment:
        TERM: "xterm-256color"

default_server: "baidu-server"
```

### 步骤4：测试连接

```bash
# 设置Python路径
export PYTHONPATH=$PWD/src:$PYTHONPATH

# 测试基本功能
python3 -m cursor_bridge.cli version

# 测试MCP服务器
echo '{"jsonrpc": "2.0", "method": "tools/call", "id": 1, "params": {"name": "execute_command", "arguments": {"command": "pwd", "server": "baidu-server"}}}' | python3 -m cursor_bridge.cli --config cursor_bridge_config.yaml mcp
```

### 步骤5：配置Cursor IDE

创建 `cursor_mcp_config.json` 文件：

```json
{
  "mcpServers": {
    "cursor-bridge": {
      "command": "python3",
      "args": [
        "-m", 
        "cursor_bridge.cli", 
        "--config", 
        "/path/to/your/cursor-bridge/cursor_bridge_config.yaml",
        "mcp"
      ],
      "env": {
        "PYTHONPATH": "/path/to/your/cursor-bridge/src"
      }
    }
  }
}
```

将此配置添加到Cursor的MCP设置中，然后重启Cursor。

### 步骤6：在Cursor中使用

现在你可以在Cursor中直接让AI Agent执行远程命令：

```
请在远程服务器上执行 ls -la 命令
请检查远程服务器的GPU状态
请在远程服务器上运行我的训练脚本
```

## 架构概览

### 工作流程示例

当Cursor Agent调用 `execute_command("nvidia-smi")` 时：

1. **cursor-bridge执行**: `tmux send-keys -t baidu-session "nvidia-smi" Enter`
2. **等待1秒让命令执行完成**
3. **捕获输出**: `tmux capture-pane -t baidu-session -p`  
4. **返回结果给Cursor Agent**

### 整体架构

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Cursor IDE    │    │  Cursor Bridge   │    │   Local tmux    │
│                 │    │      MCP         │    │    Session      │
│  ┌───────────┐  │    │  ┌─────────────┐ │    │  ┌───────────┐  │
│  │   Agent   │◄─┼────┼─►│ MCP Server  │ │    │  │ baidu-    │  │
│  └───────────┘  │    │  └─────────────┘ │    │  │ session   │  │
│                 │    │  ┌─────────────┐ │    │  └───────────┘  │
│  ┌───────────┐  │    │  │ Tmux        │◄┼────┼─►┌───────────┐  │
│  │ Terminal  │  │    │  │ Controller  │ │    │  │relay-cli  │  │
│  └───────────┘  │    │  └─────────────┘ │    │  │connection │  │
└─────────────────┘    └──────────────────┘    │  └───────────┘  │
                                               └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │  Remote Server  │
                                               │  (via relay)    │
                                               └─────────────────┘
```

## 使用示例

### CLI命令

```bash
# 查看所有可用命令
export PYTHONPATH=$PWD/src:$PYTHONPATH
python3 -m cursor_bridge.cli --help

# 启动服务器
python3 -m cursor_bridge.cli start

# 查看配置
python3 -m cursor_bridge.cli config

# 生成新配置文件
python3 -m cursor_bridge.cli init-config --output my_config.yaml
```

### MCP工具使用（开发中）

```python
# Cursor Agent 可以直接执行远程命令
await execute_command("ls -la /home/Code")
await execute_command("git status")
await execute_command("npm run build")
```

### 多服务器支持（开发中）

```python
# 在不同服务器上执行命令
await execute_command("ls", server="enterprise-dev")
await execute_command("ps aux", server="staging-server")
```

### 会话管理（开发中）

```python
# 创建新会话
await create_session("my-project", config={
    "working_directory": "/home/Code/my-project",
    "environment": {"NODE_ENV": "development"}
})

# 在特定会话中执行命令
await execute_command("npm start", session="my-project")
```

## 项目结构

```
cursor-bridge/
├── src/
│   ├── cursor_bridge/
│   │   ├── __init__.py
│   │   ├── server.py              # MCP服务器主入口
│   │   ├── connection/            # 连接管理模块
│   │   │   ├── manager.py         # 连接管理器
│   │   │   ├── strategies/        # 连接策略
│   │   │   └── pool.py           # 连接池
│   │   ├── session/              # 会话管理模块
│   │   │   ├── manager.py        # 会话管理器
│   │   │   ├── tmux.py          # tmux会话实现
│   │   │   └── buffer.py        # 输出缓冲
│   │   ├── executor/             # 命令执行模块
│   │   │   ├── command.py        # 命令执行器
│   │   │   ├── interactive.py    # 交互式命令
│   │   │   └── history.py       # 命令历史
│   │   ├── config/              # 配置管理
│   │   │   ├── models.py        # 配置数据模型
│   │   │   └── loader.py        # 配置加载器
│   │   └── utils/               # 工具模块
│   │       ├── logging.py       # 日志工具
│   │       ├── security.py      # 安全工具
│   │       └── monitoring.py    # 监控工具
├── tests/                       # 测试代码
├── config/                      # 配置文件
├── docs/                        # 文档
├── scripts/                     # 脚本工具
├── docker/                      # Docker配置
├── requirements.txt             # 依赖列表
├── pyproject.toml              # 项目配置
├── DESIGN.md                   # 设计文档
└── README.md                   # 项目说明
```

## 开发指南

### 环境准备

```bash
# 安装开发依赖
poetry install --with dev

# 安装pre-commit钩子
pre-commit install

# 运行测试
pytest

# 代码格式化
black src/ tests/
isort src/ tests/

# 类型检查
mypy src/
```

### 添加新的连接策略

```python
# src/cursor_bridge/connection/strategies/custom.py
from .base import ConnectionStrategy

class CustomConnectionStrategy(ConnectionStrategy):
    async def connect(self, config: ServerConfig) -> Connection:
        # 实现自定义连接逻辑
        pass
    
    async def health_check(self, connection: Connection) -> bool:
        # 实现健康检查
        pass
```

### 扩展MCP工具

```python
# src/cursor_bridge/tools/custom.py
from mcp import tool

@tool("custom_command")
async def custom_command(param: str) -> str:
    """自定义MCP工具"""
    # 实现自定义功能
    return result
```

## 配置参考

### 完整配置示例

```yaml
# 服务器配置
servers:
  # 通过企业VPN工具连接的服务器
  enterprise-dev:
    type: proxy
    proxy:
      command: enterprise-vpn-tool
      target_host: internal-server.company.com
      target_port: 22
      username: your-username
      timeout: 30
    session:
      name: enterprise-dev-session
      working_directory: /home/Code
      environment:
        TERM: xterm-256color
        LANG: en_US.UTF-8
      shell: /bin/bash
      
  # 直接SSH连接的服务器
  direct-server:
    type: direct
    ssh:
      host: direct-server.com
      port: 22
      username: user
      key_file: ~/.ssh/id_rsa
      timeout: 10
    session:
      name: direct-session
      working_directory: /home/user
      
  # 通过代理连接的服务器
  proxy-server:
    type: proxy
    proxy:
      host: proxy.company.com
      port: 8080
      username: proxy-user
    target:
      host: internal-server.com
      port: 22
      username: target-user

# MCP服务器配置
mcp:
  server:
    host: localhost
    port: 8082
    log_level: INFO
    max_connections: 100
    
  features:
    command_history: true
    session_persistence: true
    auto_reconnect: true
    health_check_interval: 30
    command_timeout: 300
    
  tools:
    - execute_command
    - get_session_status
    - create_session
    - destroy_session
    - list_sessions
    
  resources:
    - session_logs
    - command_history
    - server_status

# 安全配置
security:
  # 命令白名单
  allowed_commands:
    - "ls"
    - "cd"
    - "pwd"
    - "cat"
    - "grep"
    - "find"
    - "git"
    - "npm"
    - "python"
    - "make"
    - "docker"
    - "kubectl"
    
  # 命令黑名单
  blocked_commands:
    - "rm -rf /"
    - "sudo rm"
    - "mkfs"
    - "dd if="
    - ":(){ :|:& };:"
    
  # 命令模式过滤
  blocked_patterns:
    - "rm.*-rf.*/"
    - "sudo.*rm"
    - "chmod.*777"
    
  # 执行限制
  command_timeout: 300
  max_output_size: 10485760  # 10MB
  max_concurrent_commands: 10
  
  # 文件访问限制
  allowed_paths:
    - "/home"
    - "/tmp"
    - "/var/log"
    
  blocked_paths:
    - "/etc/passwd"
    - "/etc/shadow"
    - "/root"

# 监控配置
monitoring:
  metrics:
    enabled: true
    port: 9090
    path: /metrics
    
  health_check:
    enabled: true
    port: 8083
    path: /health
    
  logging:
    level: INFO
    format: json
    file: /var/log/cursor-bridge.log
    max_size: 100MB
    backup_count: 5
    
  alerts:
    connection_failure_threshold: 3
    command_timeout_threshold: 5
    error_rate_threshold: 0.1

# 性能配置
performance:
  connection_pool:
    max_size: 20
    min_size: 2
    max_idle_time: 300
    
  session_pool:
    max_sessions_per_server: 10
    session_idle_timeout: 600
    
  command_execution:
    default_timeout: 30
    max_timeout: 300
    buffer_size: 8192
    
  caching:
    command_history_size: 1000
    session_cache_ttl: 3600
```

## 部署指南

### Docker部署

```bash
# 构建镜像
docker build -t cursor-bridge .

# 运行容器
docker run -d \
  --name cursor-bridge \
  -p 8082:8082 \
  -v $(pwd)/config:/app/config \
  -v ~/.ssh:/root/.ssh:ro \
  cursor-bridge
```

### 系统服务部署

```bash
# 安装为systemd服务
sudo cp scripts/cursor-bridge.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable cursor-bridge
sudo systemctl start cursor-bridge
```

### Kubernetes部署

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cursor-bridge
spec:
  replicas: 2
  selector:
    matchLabels:
      app: cursor-bridge
  template:
    metadata:
      labels:
        app: cursor-bridge
    spec:
      containers:
      - name: cursor-bridge
        image: cursor-bridge:latest
        ports:
        - containerPort: 8082
        volumeMounts:
        - name: config
          mountPath: /app/config
      volumes:
      - name: config
        configMap:
          name: cursor-bridge-config
```

## 监控和运维

### 健康检查

```bash
# 检查服务状态
curl http://localhost:8083/health

# 检查连接状态
curl http://localhost:8083/connections

# 检查会话状态
curl http://localhost:8083/sessions
```

### 监控指标

```bash
# Prometheus指标
curl http://localhost:9090/metrics
```

主要指标：
- `cursor_bridge_connections_total`: 总连接数
- `cursor_bridge_commands_total`: 总命令执行数
- `cursor_bridge_command_duration_seconds`: 命令执行时间
- `cursor_bridge_errors_total`: 错误总数
- `cursor_bridge_sessions_active`: 活跃会话数

### 日志分析

```bash
# 查看实时日志
tail -f /var/log/cursor-bridge.log

# 查看错误日志
grep ERROR /var/log/cursor-bridge.log

# 查看命令执行日志
grep "command_executed" /var/log/cursor-bridge.log
```

## 故障排除

### 常见问题

#### 1. 连接失败
```bash
# 检查网络连通性
ping target-server.com

# 检查SSH连接
ssh -v user@target-server.com

# 检查企业VPN工具
enterprise-vpn-tool --test
```

#### 2. 命令执行超时
```yaml
# 调整超时配置
security:
  command_timeout: 600  # 增加到10分钟
```

#### 3. 会话丢失
```bash
# 检查tmux会话
tmux list-sessions

# 重新创建会话
curl -X POST http://localhost:8082/sessions/recreate
```

### 调试模式

```bash
# 启用调试日志
export LOG_LEVEL=DEBUG
python -m cursor_bridge.server

# 启用详细输出
python -m cursor_bridge.server --verbose
```

## 贡献指南

### 提交代码

1. Fork项目
2. 创建特性分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 创建Pull Request

### 代码规范

- 使用Black进行代码格式化
- 使用isort进行导入排序
- 使用mypy进行类型检查
- 编写单元测试
- 更新文档

### 报告问题

请使用GitHub Issues报告问题，包含：
- 问题描述
- 复现步骤
- 期望行为
- 实际行为
- 环境信息

## 开发状态

### ✅ 已完成 (v0.1.0)
- [x] 基础MCP服务器框架
- [x] 配置管理系统
- [x] 日志系统
- [x] CLI工具
- [x] 健康检查和监控
- [x] 自动安装脚本

### 🔄 开发中 (v0.2.0)
- [ ] 连接策略实现
- [ ] SSH连接管理
- [ ] 企业VPN工具集成
- [ ] tmux会话管理
- [ ] 基本命令执行

### 📋 计划中 (v1.0)
- [ ] 完整MCP工具实现
- [ ] Cursor IDE集成

### v1.1
- [ ] 多服务器支持
- [ ] 命令安全过滤
- [ ] 性能优化
- [ ] 监控面板

### v1.2
- [ ] 交互式命令支持
- [ ] 会话共享
- [ ] 插件系统
- [ ] Web界面

### v2.0
- [ ] 分布式部署
- [ ] 高可用架构
- [ ] 企业级安全
- [ ] 多租户支持

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 致谢

- [Model Context Protocol](https://github.com/modelcontextprotocol) - MCP协议支持
- [Cursor IDE](https://cursor.sh/) - 优秀的AI代码编辑器
- [tmux](https://github.com/tmux/tmux) - 终端复用器

## 联系我们

- 项目主页: https://github.com/maricoxu/cursor-bridge
- 问题反馈: https://github.com/maricoxu/cursor-bridge/issues
- 邮箱: maricoxu@gmail.com

---

**让远程开发像本地一样自然** 🚀