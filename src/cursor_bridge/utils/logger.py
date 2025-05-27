"""
日志系统

基于structlog的结构化日志系统。
"""

import sys
import logging
import structlog
from pathlib import Path
from typing import Optional, Dict, Any


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    json_logs: bool = False,
    service_name: str = "cursor-bridge"
) -> None:
    """设置日志系统
    
    Args:
        level: 日志级别
        log_file: 日志文件路径
        json_logs: 是否使用JSON格式
        service_name: 服务名称
    """
    # 配置标准库logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )
    
    # 配置structlog处理器
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # 如果指定了日志文件，添加文件处理器
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        
        if json_logs:
            formatter = logging.Formatter('%(message)s')
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        file_handler.setFormatter(formatter)
        
        # 添加到根日志器
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
    
    # 设置服务上下文
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(service=service_name)


def get_logger(name: str, **context: Any) -> structlog.BoundLogger:
    """获取日志器
    
    Args:
        name: 日志器名称
        **context: 额外的上下文信息
        
    Returns:
        配置好的日志器
    """
    logger = structlog.get_logger(name)
    if context:
        logger = logger.bind(**context)
    return logger


class LoggerMixin:
    """日志器混入类"""
    
    @property
    def logger(self) -> structlog.BoundLogger:
        """获取当前类的日志器"""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(
                self.__class__.__module__ + "." + self.__class__.__name__
            )
        return self._logger 