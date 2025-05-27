"""
配置数据模型

定义所有配置相关的数据结构。
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RelayConfig(BaseModel):
    """Relay连接配置"""
    command: str = "relay-cli"
    target_host: str
    target_port: int = 22
    username: str
    timeout: int = 30
    extra_args: List[str] = Field(default_factory=list)


class SSHConfig(BaseModel):
    """SSH连接配置"""
    host: str
    port: int = 22
    username: str
    key_file: Optional[str] = None
    password: Optional[str] = None
    timeout: int = 10


class SessionConfig(BaseModel):
    """会话配置"""
    name: str
    working_directory: str = "/home"
    environment: Dict[str, str] = Field(default_factory=dict)
    shell: str = "/bin/bash"


class ServerConfig(BaseModel):
    """服务器配置"""
    type: str  # relay, direct, proxy
    relay: Optional[RelayConfig] = None
    ssh: Optional[SSHConfig] = None
    session: SessionConfig


class MCPConfig(BaseModel):
    """MCP服务器配置"""
    server: Dict[str, Any] = Field(default_factory=dict)
    features: Dict[str, Any] = Field(default_factory=dict)
    tools: List[str] = Field(default_factory=list)
    resources: List[str] = Field(default_factory=list)


class SecurityConfig(BaseModel):
    """安全配置"""
    allowed_commands: List[str] = Field(default_factory=list)
    blocked_commands: List[str] = Field(default_factory=list)
    blocked_patterns: List[str] = Field(default_factory=list)
    command_timeout: int = 300
    max_output_size: int = 10485760
    max_concurrent_commands: int = 10
    allowed_paths: List[str] = Field(default_factory=list)
    blocked_paths: List[str] = Field(default_factory=list)


class MonitoringConfig(BaseModel):
    """监控配置"""
    metrics: Dict[str, Any] = Field(default_factory=dict)
    health_check: Dict[str, Any] = Field(default_factory=dict)
    logging: Dict[str, Any] = Field(default_factory=dict)


class PerformanceConfig(BaseModel):
    """性能配置"""
    connection_pool: Dict[str, Any] = Field(default_factory=dict)
    session_pool: Dict[str, Any] = Field(default_factory=dict)
    command_execution: Dict[str, Any] = Field(default_factory=dict)
    caching: Dict[str, Any] = Field(default_factory=dict)


class CursorBridgeConfig(BaseModel):
    """Cursor Bridge完整配置"""
    servers: Dict[str, ServerConfig]
    mcp: MCPConfig = Field(default_factory=MCPConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)