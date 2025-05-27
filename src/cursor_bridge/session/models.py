"""
会话数据模型

定义会话相关的数据结构和枚举。
"""

import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime


class SessionStatus(Enum):
    """会话状态枚举"""
    CREATING = "creating"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DESTROYED = "destroyed"
    ERROR = "error"


class SessionType(Enum):
    """会话类型枚举"""
    INTERACTIVE = "interactive"  # 交互式会话
    PERSISTENT = "persistent"    # 持久化会话
    TEMPORARY = "temporary"      # 临时会话


@dataclass
class SessionConfig:
    """会话配置"""
    name: str
    server_name: str
    session_type: SessionType = SessionType.INTERACTIVE
    working_directory: Optional[str] = None
    environment: Dict[str, str] = field(default_factory=dict)
    shell: str = "/bin/bash"
    auto_restart: bool = True
    max_idle_time: int = 3600  # 最大空闲时间（秒）
    persist_history: bool = True
    max_history_size: int = 10000


@dataclass
class SessionInfo:
    """会话信息"""
    name: str
    server_name: str
    status: SessionStatus
    session_type: SessionType
    created_at: float
    last_activity: float
    pid: Optional[int] = None
    working_directory: Optional[str] = None
    command_count: int = 0
    error_message: Optional[str] = None
    
    @property
    def uptime(self) -> float:
        """获取会话运行时间"""
        return time.time() - self.created_at
    
    @property
    def idle_time(self) -> float:
        """获取空闲时间"""
        return time.time() - self.last_activity
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'name': self.name,
            'server_name': self.server_name,
            'status': self.status.value,
            'session_type': self.session_type.value,
            'created_at': self.created_at,
            'last_activity': self.last_activity,
            'uptime': self.uptime,
            'idle_time': self.idle_time,
            'pid': self.pid,
            'working_directory': self.working_directory,
            'command_count': self.command_count,
            'error_message': self.error_message
        }


@dataclass
class CommandResult:
    """命令执行结果"""
    command: str
    exit_code: int
    stdout: str
    stderr: str
    execution_time: float
    timestamp: float = field(default_factory=time.time)
    
    @property
    def success(self) -> bool:
        """命令是否执行成功"""
        return self.exit_code == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'command': self.command,
            'exit_code': self.exit_code,
            'stdout': self.stdout,
            'stderr': self.stderr,
            'execution_time': self.execution_time,
            'timestamp': self.timestamp,
            'success': self.success
        }


@dataclass
class SessionStats:
    """会话统计信息"""
    total_sessions: int = 0
    active_sessions: int = 0
    inactive_sessions: int = 0
    suspended_sessions: int = 0
    error_sessions: int = 0
    total_commands_executed: int = 0
    average_session_uptime: float = 0.0
    average_command_execution_time: float = 0.0
    last_cleanup_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'total_sessions': self.total_sessions,
            'active_sessions': self.active_sessions,
            'inactive_sessions': self.inactive_sessions,
            'suspended_sessions': self.suspended_sessions,
            'error_sessions': self.error_sessions,
            'total_commands_executed': self.total_commands_executed,
            'average_session_uptime': self.average_session_uptime,
            'average_command_execution_time': self.average_command_execution_time,
            'last_cleanup_time': self.last_cleanup_time
        }