"""
Cursor Bridge - 无缝远程开发桥梁

为Cursor IDE提供企业级远程终端访问解决方案的MCP服务器。
"""

__version__ = "0.1.0"
__author__ = "maricoxu"
__email__ = "maricoxu@gmail.com"
__license__ = "MIT"

from .server import CursorBridgeServer
from .config.models import ServerConfig, MCPConfig, SecurityConfig
from .connection.manager import ConnectionManager
from .session.manager import SessionManager
from .executor.command import CommandExecutor

__all__ = [
    "CursorBridgeServer",
    "ServerConfig",
    "MCPConfig", 
    "SecurityConfig",
    "ConnectionManager",
    "SessionManager",
    "CommandExecutor",
]