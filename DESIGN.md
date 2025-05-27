# Terminal Agent MCP - 设计文档

## 项目概述

**Terminal Agent MCP** 是一个基于Model Context Protocol (MCP)的远程终端代理系统，旨在为Cursor IDE提供无缝的远程服务器终端访问能力。该项目解决了企业内网开发中需要通过跳板机或企业VPN工具访问远程服务器的复杂性问题。

### 核心价值
- 🚀 **无缝体验**：Cursor Agent可以直接在远程服务器上执行命令
- 🔄 **连接复用**：一次连接，持续使用，避免重复认证
- 🛡️ **安全可靠**：基于现有的企业安全架构
- 🎯 **开发友好**：保持原生终端体验，无学习成本

## 架构设计

### 整体架构

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Cursor IDE    │    │  Terminal Agent  │    │  Remote Server  │
│                 │    │      MCP         │    │                 │
│  ┌───────────┐  │    │  ┌─────────────┐ │    │  ┌───────────┐  │
│  │   Agent   │◄─┼────┼─►│ MCP Server  │ │    │  │   tmux    │  │
│  └───────────┘  │    │  └─────────────┘ │    │  │ Session   │  │
│                 │    │  ┌─────────────┐ │    │  └───────────┘  │
│  ┌───────────┐  │    │  │ Connection  │◄┼────┼─►┌───────────┐  │
│  │ Terminal  │  │    │  │  Manager    │ │    │  │   Shell   │  │
│  └───────────┘  │    │  └─────────────┘ │    │  └───────────┘  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Proxy/VPN      │
                       │ (enterprise-vpn) │
                       └──────────────────┘
```

### 核心组件

#### 1. MCP Server (核心服务)
- **职责**：提供MCP协议接口，处理Cursor Agent的请求
- **功能**：
  - 接收命令执行请求
  - 管理会话状态
  - 返回执行结果
  - 处理错误和异常

#### 2. Connection Manager (连接管理器)
- **职责**：管理到远程服务器的连接
- **功能**：
  - 自动建立和维护连接
  - 连接健康检查
  - 断线重连
  - 多服务器支持

#### 3. Session Manager (会话管理器)
- **职责**：管理远程tmux会话
- **功能**：
  - 创建和销毁会话
  - 会话状态监控
  - 命令队列管理
  - 输出缓冲处理

#### 4. Command Executor (命令执行器)
- **职责**：在远程会话中执行命令
- **功能**：
  - 命令发送和执行
  - 输出捕获和解析
  - 交互式命令支持
  - 执行状态跟踪

## 技术方案

### 方案1与方案2的关系

**方案1（智能连接管理）** 作为基础设施层：
- 负责建立和维护到远程服务器的基础连接
- 提供端口转发和网络通道
- 处理企业VPN工具的复杂性

**方案2（Agent远程执行）** 作为应用层：
- 基于方案1建立的连接通道
- 提供MCP协议接口
- 实现命令的透明执行

### 分层架构

```
┌─────────────────────────────────────────┐
│           Application Layer             │  ← 方案2: MCP Server + Agent Integration
│  (MCP Protocol, Command Execution)     │
├─────────────────────────────────────────┤
│          Infrastructure Layer          │  ← 方案1: Connection Management
│  (Connection, Tunneling, Session)      │
├─────────────────────────────────────────┤
│            Network Layer               │
│  (enterprise-vpn, SSH, Port Forwarding) │
└─────────────────────────────────────────┘
```

## 详细设计

### 1. MCP Server 设计

#### 接口定义
```python
class TerminalAgentMCP:
    @tool("execute_command")
    async def execute_command(
        self, 
        command: str, 
        server: str = "default",
        timeout: int = 30,
        interactive: bool = False
    ) -> CommandResult
    
    @tool("get_session_status")
    async def get_session_status(self, server: str = "default") -> SessionStatus
    
    @tool("create_session")
    async def create_session(self, server: str, config: ServerConfig) -> bool
    
    @tool("destroy_session")
    async def destroy_session(self, server: str) -> bool
    
    @resource("session_logs")
    async def get_session_logs(self, server: str) -> str
```

#### 数据模型
```python
@dataclass
class CommandResult:
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float
    command: str
    timestamp: datetime

@dataclass
class SessionStatus:
    server: str
    connected: bool
    session_id: str
    uptime: float
    last_activity: datetime

@dataclass
class ServerConfig:
    name: str
    host: str
    port: int
    username: str
    connection_type: str  # "direct", "proxy", "vpn"
    proxy_config: Optional[ProxyConfig] = None
```

### 2. Connection Manager 设计

#### 连接策略
```python
class ConnectionStrategy(ABC):
    @abstractmethod
    async def connect(self, config: ServerConfig) -> Connection
    
    @abstractmethod
    async def health_check(self, connection: Connection) -> bool
    
    @abstractmethod
    async def reconnect(self, connection: Connection) -> bool

class ProxyConnectionStrategy(ConnectionStrategy):
    """基于企业VPN工具的连接策略"""
    
class DirectConnectionStrategy(ConnectionStrategy):
    """直接SSH连接策略"""
    
class VPNConnectionStrategy(ConnectionStrategy):
    """VPN连接策略"""
```

#### 连接池管理
```python
class ConnectionPool:
    def __init__(self, max_connections: int = 10):
        self.connections: Dict[str, Connection] = {}
        self.strategies: Dict[str, ConnectionStrategy] = {}
    
    async def get_connection(self, server: str) -> Connection:
        """获取或创建连接"""
        
    async def health_check_all(self) -> Dict[str, bool]:
        """检查所有连接健康状态"""
        
    async def cleanup_stale_connections(self):
        """清理失效连接"""
```

### 3. Session Manager 设计

#### tmux会话管理
```python
class TmuxSessionManager:
    def __init__(self, connection: Connection):
        self.connection = connection
        self.sessions: Dict[str, TmuxSession] = {}
    
    async def create_session(self, name: str, config: SessionConfig) -> TmuxSession:
        """创建新的tmux会话"""
        
    async def get_session(self, name: str) -> Optional[TmuxSession]:
        """获取现有会话"""
        
    async def list_sessions(self) -> List[str]:
        """列出所有会话"""
        
    async def destroy_session(self, name: str) -> bool:
        """销毁会话"""

class TmuxSession:
    def __init__(self, name: str, connection: Connection):
        self.name = name
        self.connection = connection
        self.command_queue = asyncio.Queue()
        self.output_buffer = OutputBuffer()
    
    async def execute_command(self, command: str, timeout: int = 30) -> CommandResult:
        """在会话中执行命令"""
        
    async def send_keys(self, keys: str):
        """发送按键到会话"""
        
    async def capture_output(self) -> str:
        """捕获会话输出"""
```

### 4. Command Executor 设计

#### 命令执行流程
```python
class CommandExecutor:
    def __init__(self, session: TmuxSession):
        self.session = session
        self.execution_history: List[CommandResult] = []
    
    async def execute(self, command: str, options: ExecutionOptions) -> CommandResult:
        """执行命令的主要流程"""
        # 1. 预处理命令
        processed_command = await self.preprocess_command(command)
        
        # 2. 发送命令到远程会话
        execution_id = await self.send_command(processed_command)
        
        # 3. 等待执行完成
        result = await self.wait_for_completion(execution_id, options.timeout)
        
        # 4. 后处理结果
        final_result = await self.postprocess_result(result)
        
        # 5. 记录历史
        self.execution_history.append(final_result)
        
        return final_result
    
    async def execute_interactive(self, command: str) -> AsyncIterator[str]:
        """执行交互式命令，流式返回输出"""
```

## 配置系统

### 配置文件结构
```yaml
# terminal_agent_config.yaml
servers:
  enterprise-dev:
    type: proxy
    proxy:
      command: enterprise-vpn-tool
      target_host: internal-server.company.com
      target_port: 22
      username: your-username
    session:
      name: enterprise-dev-session
      working_directory: /home/Code
      environment:
        TERM: xterm-256color
        
  direct-server:
    type: direct
    ssh:
      host: direct-server.com
      port: 22
      username: user
      key_file: ~/.ssh/id_rsa
    session:
      name: direct-session
      working_directory: /home/user

mcp:
  server:
    host: localhost
    port: 8082
    log_level: INFO
  
  features:
    command_history: true
    session_persistence: true
    auto_reconnect: true
    health_check_interval: 30

security:
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
  
  blocked_commands:
    - "rm -rf /"
    - "sudo rm"
    - "mkfs"
  
  command_timeout: 300
  max_output_size: 10485760  # 10MB
```

## 实现计划

### Phase 1: 核心基础设施 (Week 1-2)
- [ ] 项目结构搭建
- [ ] MCP Server基础框架
- [ ] Connection Manager基础实现
- [ ] 配置系统
- [ ] 基础测试框架

### Phase 2: 连接管理 (Week 3-4)
- [ ] RelayConnectionStrategy实现
- [ ] 连接池管理
- [ ] 健康检查机制
- [ ] 断线重连逻辑
- [ ] 连接状态监控

### Phase 3: 会话管理 (Week 5-6)
- [ ] TmuxSessionManager实现
- [ ] 会话创建和销毁
- [ ] 会话状态管理
- [ ] 输出缓冲处理
- [ ] 会话持久化

### Phase 4: 命令执行 (Week 7-8)
- [ ] CommandExecutor实现
- [ ] 同步命令执行
- [ ] 异步命令执行
- [ ] 交互式命令支持
- [ ] 命令历史记录

### Phase 5: 集成和优化 (Week 9-10)
- [ ] Cursor MCP集成
- [ ] 性能优化
- [ ] 错误处理完善
- [ ] 日志系统
- [ ] 文档完善

### Phase 6: 高级功能 (Week 11-12)
- [ ] 多服务器支持
- [ ] 命令安全过滤
- [ ] 会话共享
- [ ] 监控和告警
- [ ] 部署自动化

## 技术栈

### 核心技术
- **Python 3.9+**: 主要开发语言
- **asyncio**: 异步编程框架
- **MCP SDK**: Model Context Protocol实现
- **pexpect**: 终端自动化
- **paramiko**: SSH连接管理
- **pydantic**: 数据验证和序列化

### 开发工具
- **pytest**: 单元测试
- **black**: 代码格式化
- **mypy**: 类型检查
- **pre-commit**: Git钩子管理
- **poetry**: 依赖管理

### 部署和运维
- **Docker**: 容器化部署
- **systemd**: 系统服务管理
- **prometheus**: 监控指标
- **grafana**: 监控面板

## 安全考虑

### 1. 命令安全
- 命令白名单/黑名单机制
- 危险命令拦截
- 命令参数验证
- 执行权限控制

### 2. 连接安全
- SSH密钥管理
- 连接加密
- 认证信息保护
- 会话隔离

### 3. 数据安全
- 敏感信息脱敏
- 日志安全存储
- 输出内容过滤
- 数据传输加密

## 监控和运维

### 1. 健康检查
- 连接状态监控
- 会话健康检查
- 服务可用性监控
- 性能指标收集

### 2. 日志管理
- 结构化日志
- 日志级别控制
- 日志轮转
- 错误告警

### 3. 性能监控
- 命令执行时间
- 连接延迟
- 内存使用
- CPU使用率

## 扩展性设计

### 1. 插件系统
- 连接策略插件
- 命令处理插件
- 输出格式化插件
- 安全策略插件

### 2. 协议扩展
- 自定义MCP工具
- 自定义MCP资源
- 协议版本兼容
- 向后兼容性

### 3. 多平台支持
- Windows支持
- Linux支持
- macOS支持
- 容器化部署

## 测试策略

### 1. 单元测试
- 组件独立测试
- Mock外部依赖
- 边界条件测试
- 错误场景测试

### 2. 集成测试
- 端到端测试
- 多服务器测试
- 并发测试
- 压力测试

### 3. 用户验收测试
- Cursor集成测试
- 用户场景测试
- 性能基准测试
- 兼容性测试

## 文档计划

### 1. 开发文档
- API文档
- 架构文档
- 部署指南
- 故障排除

### 2. 用户文档
- 快速开始
- 配置指南
- 使用教程
- 最佳实践

### 3. 运维文档
- 部署手册
- 监控指南
- 备份恢复
- 安全配置

## 成功指标

### 1. 功能指标
- [ ] 支持企业VPN工具连接方式
- [ ] 命令执行成功率 > 99%
- [ ] 连接建立时间 < 5秒
- [ ] 命令响应时间 < 1秒

### 2. 可靠性指标
- [ ] 系统可用性 > 99.9%
- [ ] 自动重连成功率 > 95%
- [ ] 错误恢复时间 < 30秒
- [ ] 数据丢失率 = 0%

### 3. 用户体验指标
- [ ] Cursor集成无缝
- [ ] 学习成本接近0
- [ ] 配置时间 < 10分钟
- [ ] 用户满意度 > 90%

## 风险评估

### 1. 技术风险
- **MCP协议变更**: 中等风险，需要持续跟进协议更新
- **网络连接不稳定**: 高风险，需要强化重连机制
- **性能瓶颈**: 中等风险，需要性能测试和优化

### 2. 安全风险
- **命令注入**: 高风险，需要严格的输入验证
- **权限提升**: 中等风险，需要最小权限原则
- **数据泄露**: 中等风险，需要数据加密和脱敏

### 3. 运维风险
- **服务依赖**: 中等风险，需要降级方案
- **配置复杂**: 低风险，提供默认配置和向导
- **维护成本**: 中等风险，需要自动化运维

## 总结

Terminal Agent MCP项目通过分层架构设计，将复杂的企业内网访问问题分解为可管理的组件。基于方案1的连接管理基础设施，构建方案2的MCP服务层，为Cursor IDE提供无缝的远程终端访问能力。

项目的核心价值在于：
1. **简化复杂性**：将企业VPN工具的复杂性封装在底层
2. **提升体验**：为开发者提供原生终端体验
3. **保证可靠性**：通过连接池和重连机制确保稳定性
4. **确保安全性**：通过多层安全机制保护系统安全

通过12周的分阶段实施计划，项目将逐步构建完整的远程终端代理系统，最终实现"让工具适应工作流程"的设计哲学。