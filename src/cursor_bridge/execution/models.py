"""
命令执行数据模型

定义命令执行相关的数据结构和枚举。
"""

import time
import uuid
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime


class ExecutionStatus(Enum):
    """执行状态枚举"""
    PENDING = "pending"      # 等待执行
    RUNNING = "running"      # 正在执行
    COMPLETED = "completed"  # 执行完成
    FAILED = "failed"        # 执行失败
    TIMEOUT = "timeout"      # 执行超时
    CANCELLED = "cancelled"  # 被取消
    RETRYING = "retrying"    # 重试中


class ExecutionPriority(Enum):
    """执行优先级枚举"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class OutputFormat(Enum):
    """输出格式枚举"""
    RAW = "raw"              # 原始输出
    JSON = "json"            # JSON格式
    STRUCTURED = "structured" # 结构化输出
    FILTERED = "filtered"    # 过滤输出


@dataclass
class ExecutionOptions:
    """执行选项配置"""
    timeout: Optional[int] = 30                    # 超时时间（秒）
    priority: ExecutionPriority = ExecutionPriority.NORMAL
    retry_count: int = 0                          # 重试次数
    retry_delay: float = 1.0                      # 重试延迟（秒）
    capture_output: bool = True                   # 是否捕获输出
    stream_output: bool = False                   # 是否流式输出
    working_directory: Optional[str] = None       # 工作目录
    environment: Dict[str, str] = field(default_factory=dict)  # 环境变量
    shell: bool = True                           # 是否使用shell
    output_format: OutputFormat = OutputFormat.RAW
    max_output_size: int = 1024 * 1024          # 最大输出大小（字节）
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'timeout': self.timeout,
            'priority': self.priority.value,
            'retry_count': self.retry_count,
            'retry_delay': self.retry_delay,
            'capture_output': self.capture_output,
            'stream_output': self.stream_output,
            'working_directory': self.working_directory,
            'environment': self.environment,
            'shell': self.shell,
            'output_format': self.output_format.value,
            'max_output_size': self.max_output_size
        }


@dataclass
class ExecutionContext:
    """执行上下文"""
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_name: str = ""
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'execution_id': self.execution_id,
            'session_name': self.session_name,
            'user_id': self.user_id,
            'request_id': self.request_id,
            'tags': self.tags,
            'metadata': self.metadata,
            'created_at': self.created_at
        }


@dataclass
class CommandExecution:
    """命令执行记录"""
    context: ExecutionContext
    command: str
    options: ExecutionOptions
    status: ExecutionStatus = ExecutionStatus.PENDING
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    exit_code: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    error_message: Optional[str] = None
    retry_attempts: int = 0
    
    @property
    def execution_time(self) -> Optional[float]:
        """获取执行时间"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    @property
    def is_running(self) -> bool:
        """是否正在执行"""
        return self.status == ExecutionStatus.RUNNING
    
    @property
    def is_completed(self) -> bool:
        """是否已完成"""
        return self.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, 
                              ExecutionStatus.TIMEOUT, ExecutionStatus.CANCELLED]
    
    @property
    def is_successful(self) -> bool:
        """是否执行成功"""
        return self.status == ExecutionStatus.COMPLETED and self.exit_code == 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'context': self.context.to_dict(),
            'command': self.command,
            'options': self.options.to_dict(),
            'status': self.status.value,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'execution_time': self.execution_time,
            'exit_code': self.exit_code,
            'stdout': self.stdout,
            'stderr': self.stderr,
            'error_message': self.error_message,
            'retry_attempts': self.retry_attempts,
            'is_successful': self.is_successful
        }


# 回调函数类型定义
OutputCallback = Callable[[str, str], None]  # (stdout, stderr) -> None
StatusCallback = Callable[[ExecutionStatus], None]  # status -> None
ProgressCallback = Callable[[int, int], None]  # (completed, total) -> None