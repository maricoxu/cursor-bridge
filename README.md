# Cursor Bridge

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub repo](https://img.shields.io/badge/GitHub-cursor--bridge-blue.svg)](https://github.com/maricoxu/cursor-bridge)

🚀 **无缝远程开发桥梁** - 为Cursor IDE提供企业级远程终端访问解决方案

## 项目简介

Cursor Bridge 是一个基于Model Context Protocol (MCP)的远程终端代理系统，专门解决企业内网开发中通过企业VPN工具或跳板机访问远程服务器的复杂性问题。让Cursor的AI Agent能够直接在远程服务器上执行命令，就像在本地一样自然。

### ✨ 核心特性

- 🔄 **连接复用**: 一次连接，持续使用，告别重复认证
- 🎯 **无缝集成**: Cursor Agent直接在远程服务器执行命令
- 🛡️ **企业安全**: 基于现有安全架构，支持跳板机访问
- ⚡ **高性能**: 异步架构，毫秒级响应
- 🔧 **易配置**: YAML配置，开箱即用
- 📊 **可观测**: 完整的监控和日志系统

## 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/maricoxu/cursor-bridge.git
cd cursor-bridge

# 安装依赖
pip install -r requirements.txt

# 或使用poetry
poetry install
```

### 配置

```yaml
# config/cursor_bridge_config.yaml
servers:
  enterprise-dev:
    type: proxy
    proxy:
      command: enterprise-vpn-tool
      target_host: your-server.com
      target_port: 22
      username: your-username
    session:
      name: enterprise-dev-session
      working_directory: /home/Code
```

### 启动服务

```bash
# 启动MCP服务器
python -m cursor_bridge.server --config config/cursor_bridge_config.yaml

# 或使用Docker
docker run -d -p 8082:8082 -v $(pwd)/config:/app/config cursor-bridge
```

### Cursor集成

在Cursor中配置MCP服务器：

```json
{
  "mcpServers": {
    "cursor-bridge": {
      "command": "python",
      "args": ["-m", "cursor_bridge.server"],
      "env": {
        "CONFIG_PATH": "/path/to/config/cursor_bridge_config.yaml"
      }
    }
  }
}
```

## 架构概览

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Cursor IDE    │    │  Cursor Bridge   │    │  Remote Server  │
│                 │    │      MCP         │    │                 │
│  ┌───────────┐  │    │  ┌─────────────┐ │    │  ┌───────────┐  │
│  │   Agent   │◄─┼────┼─►│ MCP Server  │ │    │  │   tmux    │  │
│  └───────────┘  │    │  └─────────────┘ │    │  │ Session   │  │
│                 │    │  ┌─────────────┐ │    │  └───────────┘  │
│  ┌───────────┐  │    │  │ Connection  │◄┼────┼─►┌───────────┐  │
│  │ Terminal  │  │    │  │  Manager    │ │    │  │   Shell   │  │
│  └───────────┘  │    │  └─────────────┘ │    │  └───────────┘  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 使用示例

### 基本命令执行

```python
# Cursor Agent 可以直接执行远程命令
await execute_command("ls -la /home/Code")
await execute_command("git status")
await execute_command("npm run build")
```

### 多服务器支持

```python
# 在不同服务器上执行命令
await execute_command("ls", server="enterprise-dev")
await execute_command("ps aux", server="staging-server")
```

### 会话管理

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

## 路线图

### v1.0 (当前开发中)
- [x] 基础MCP服务器框架
- [x] 企业VPN工具连接支持
- [x] tmux会话管理
- [ ] 基本命令执行
- [ ] Cursor集成

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