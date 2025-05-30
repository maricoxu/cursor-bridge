"""
Cursor Bridge MCP服务器实现

基于MCP协议的真正服务器实现，提供工具和资源。
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional, Sequence
from pathlib import Path
import logging

# 由于MCP需要Python 3.10+，我们先用基础实现
# from mcp.server import Server
# from mcp.server.models import InitializationOptions
# from mcp.server.stdio import stdio_server
# from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from .config import ConfigLoader, CursorBridgeConfig
from .utils import setup_logging, get_logger, LoggerMixin
from .connection import ConnectionManager


class MCPServer(LoggerMixin):
    """MCP协议服务器实现"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化MCP服务器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_loader = ConfigLoader()
        self.config: Optional[CursorBridgeConfig] = None
        self.connection_manager = ConnectionManager()
        
        # 加载配置
        if config_path:
            self.config = self.config_loader.load_from_file(config_path)
        else:
            try:
                self.config = self.config_loader.load_from_env()
            except FileNotFoundError:
                self.logger.warning("未找到配置文件，使用默认配置")
                self.config = CursorBridgeConfig(servers={})
    
    async def execute_command(
        self, 
        command: str, 
        server: str = "default",
        timeout: int = 30,
        working_directory: Optional[str] = None
    ) -> Dict[str, Any]:
        """执行远程命令
        
        Args:
            command: 要执行的命令
            server: 服务器名称
            timeout: 超时时间（秒）
            working_directory: 工作目录
            
        Returns:
            命令执行结果
        """
        self.logger.info("执行命令", command=command, server=server)
        
        # 获取服务器配置
        if server == "default":
            # 使用配置中的默认服务器
            if hasattr(self.config, 'default_server') and self.config.default_server:
                server = self.config.default_server
            else:
                # 如果没有指定默认服务器，使用第一个服务器
                if self.config.servers:
                    server = list(self.config.servers.keys())[0]
                else:
                    return {
                        "stdout": "",
                        "stderr": "未配置任何服务器",
                        "exit_code": 1,
                        "execution_time": 0,
                        "command": command,
                        "server": server
                    }
        
        if server not in self.config.servers:
            return {
                "stdout": "",
                "stderr": f"服务器 '{server}' 不存在",
                "exit_code": 1,
                "execution_time": 0,
                "command": command,
                "server": server
            }
        
        server_config = self.config.servers[server]
        
        # 检查服务器类型，目前只支持local_tmux
        if server_config.type != "local_tmux":
            return {
                "stdout": "",
                "stderr": f"服务器类型 '{server_config.type}' 暂不支持",
                "exit_code": 1,
                "execution_time": 0,
                "command": command,
                "server": server
            }
        
        try:
            # 导入tmux后端
            from .session.tmux_backend import tmux_backend
            
            # 获取tmux配置
            tmux_config = getattr(server_config, 'tmux', None)
            if not tmux_config:
                return {
                    "stdout": "",
                    "stderr": f"服务器 '{server}' 缺少tmux配置",
                    "exit_code": 1,
                    "execution_time": 0,
                    "command": command,
                    "server": server
                }
            
            session_name = tmux_config.session_name
            window_name = getattr(tmux_config, 'window_name', 'main')
            
            # 获取tmux会话
            tmux_session = tmux_backend.get_session(session_name, window_name)
            
            # 检查会话是否存在
            if not await tmux_session.check_session_exists():
                return {
                    "stdout": "",
                    "stderr": f"tmux会话 '{session_name}' 不存在，请先手动创建并连接到远程服务器",
                    "exit_code": 1,
                    "execution_time": 0,
                    "command": command,
                    "server": server
                }
            
            # 如果指定了工作目录，先切换目录
            if working_directory:
                cd_command = f"cd {working_directory}"
                await tmux_session.send_command(cd_command, wait_time=0.5)
            
            # 执行命令
            result = await tmux_session.send_command(command, wait_time=1.0)
            
            # 添加服务器信息
            result["server"] = server
            result["working_directory"] = working_directory
            
            return result
            
        except Exception as e:
            self.logger.error("执行命令失败", error=str(e))
            return {
                "stdout": "",
                "stderr": f"执行命令失败: {str(e)}",
                "exit_code": 1,
                "execution_time": 0,
                "command": command,
                "server": server
            }
    
    async def list_sessions(self, server: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出会话
        
        Args:
            server: 服务器名称，None表示所有服务器
            
        Returns:
            会话列表
        """
        self.logger.info("列出会话", server=server)
        
        # TODO: 实现真正的会话列表逻辑
        sessions = []
        
        if server:
            if server in self.config.servers:
                sessions.append({
                    "server": server,
                    "session_id": f"{server}-session",
                    "status": "active",
                    "created_at": "2024-01-01T00:00:00Z",
                    "last_activity": "2024-01-01T00:00:00Z"
                })
        else:
            for server_name in self.config.servers.keys():
                sessions.append({
                    "server": server_name,
                    "session_id": f"{server_name}-session",
                    "status": "active",
                    "created_at": "2024-01-01T00:00:00Z",
                    "last_activity": "2024-01-01T00:00:00Z"
                })
        
        return sessions
    
    async def create_session(
        self, 
        server: str, 
        session_name: Optional[str] = None,
        working_directory: Optional[str] = None
    ) -> Dict[str, Any]:
        """创建新会话
        
        Args:
            server: 服务器名称
            session_name: 会话名称
            working_directory: 工作目录
            
        Returns:
            创建的会话信息
        """
        self.logger.info("创建会话", server=server, session_name=session_name)
        
        if server not in self.config.servers:
            raise ValueError(f"服务器 {server} 不存在")
        
        # TODO: 实现真正的会话创建逻辑
        session_id = session_name or f"{server}-session-{int(asyncio.get_event_loop().time())}"
        
        return {
            "server": server,
            "session_id": session_id,
            "status": "created",
            "working_directory": working_directory or "/home",
            "created_at": "2024-01-01T00:00:00Z"
        }
    
    async def destroy_session(self, server: str, session_id: str) -> bool:
        """销毁会话
        
        Args:
            server: 服务器名称
            session_id: 会话ID
            
        Returns:
            是否成功销毁
        """
        self.logger.info("销毁会话", server=server, session_id=session_id)
        
        # TODO: 实现真正的会话销毁逻辑
        return True
    
    async def get_session_status(self, server: str, session_id: str) -> Dict[str, Any]:
        """获取会话状态
        
        Args:
            server: 服务器名称
            session_id: 会话ID
            
        Returns:
            会话状态信息
        """
        self.logger.info("获取会话状态", server=server, session_id=session_id)
        
        # TODO: 实现真正的会话状态查询逻辑
        return {
            "server": server,
            "session_id": session_id,
            "status": "active",
            "uptime": 3600,
            "last_activity": "2024-01-01T00:00:00Z",
            "working_directory": "/home",
            "environment": {}
        }
    
    async def get_server_status(self) -> Dict[str, Any]:
        """获取服务器状态
        
        Returns:
            服务器状态信息
        """
        self.logger.info("获取服务器状态")
        
        servers_status = {}
        for server_name, server_config in self.config.servers.items():
            servers_status[server_name] = {
                "type": server_config.type,
                "status": "connected",  # TODO: 实现真正的连接状态检查
                "last_check": "2024-01-01T00:00:00Z"
            }
        
        return {
            "total_servers": len(self.config.servers),
            "active_servers": len(self.config.servers),
            "servers": servers_status
        }


# 简化的MCP协议处理器（不依赖mcp包）
class SimpleMCPHandler:
    """简化的MCP协议处理器"""
    
    def __init__(self, mcp_server: MCPServer):
        self.mcp_server = mcp_server
        self.logger = get_logger("mcp-handler")
        self.initialized = False
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理MCP请求
        
        Args:
            request: MCP请求
            
        Returns:
            MCP响应
        """
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        self.logger.info("处理MCP请求", method=method, request_id=request_id)
        
        try:
            if method == "initialize":
                return await self._handle_initialize(request_id, params)
            elif method == "initialized":
                return await self._handle_initialized(request_id)
            elif method == "tools/list":
                return await self._handle_tools_list(request_id)
            elif method == "tools/call":
                return await self._handle_tools_call(request_id, params)
            elif method == "resources/list":
                return await self._handle_resources_list(request_id)
            elif method == "resources/read":
                return await self._handle_resources_read(request_id, params)
            else:
                return self._error_response(request_id, -32601, f"Method not found: {method}")
                
        except Exception as e:
            self.logger.error("处理请求失败", method=method, error=str(e))
            return self._error_response(request_id, -32603, f"Internal error: {str(e)}")
    
    async def _handle_initialize(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理初始化请求"""
        self.logger.info("处理初始化请求", params=params)
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "serverInfo": {
                    "name": "cursor-bridge",
                    "version": "0.1.0"
                }
            }
        }
    
    async def _handle_initialized(self, request_id: Any) -> Dict[str, Any]:
        """处理初始化完成通知"""
        self.logger.info("MCP初始化完成")
        self.initialized = True
        
        # 对于通知，不需要返回响应
        return None
    
    async def _handle_tools_list(self, request_id: Any) -> Dict[str, Any]:
        """处理工具列表请求"""
        self.logger.info("处理工具列表请求")
        
        tools = [
            {
                "name": "execute_command",
                "description": "在远程服务器上执行命令",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "要执行的命令"
                        },
                        "server": {
                            "type": "string",
                            "description": "服务器名称",
                            "default": "baidu-server"
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "超时时间（秒）",
                            "default": 30
                        },
                        "working_directory": {
                            "type": "string",
                            "description": "工作目录"
                        }
                    },
                    "required": ["command"]
                }
            },
            {
                "name": "list_sessions",
                "description": "列出活跃的会话",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "server": {
                            "type": "string",
                            "description": "服务器名称，留空表示所有服务器"
                        }
                    }
                }
            },
            {
                "name": "create_session",
                "description": "创建新的会话",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "server": {
                            "type": "string",
                            "description": "服务器名称"
                        },
                        "session_name": {
                            "type": "string",
                            "description": "会话名称"
                        },
                        "working_directory": {
                            "type": "string",
                            "description": "工作目录"
                        }
                    },
                    "required": ["server"]
                }
            },
            {
                "name": "get_session_status",
                "description": "获取会话状态",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "server": {
                            "type": "string",
                            "description": "服务器名称"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "会话ID"
                        }
                    },
                    "required": ["server", "session_id"]
                }
            }
        ]
        
        self.logger.info("返回工具列表", tool_count=len(tools))
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools
            }
        }
    
    async def _handle_tools_call(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理工具调用请求"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "execute_command":
            result = await self.mcp_server.execute_command(**arguments)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2, ensure_ascii=False)
                        }
                    ]
                }
            }
        elif tool_name == "list_sessions":
            result = await self.mcp_server.list_sessions(**arguments)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2, ensure_ascii=False)
                        }
                    ]
                }
            }
        elif tool_name == "create_session":
            result = await self.mcp_server.create_session(**arguments)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2, ensure_ascii=False)
                        }
                    ]
                }
            }
        elif tool_name == "destroy_session":
            result = await self.mcp_server.destroy_session(**arguments)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"会话销毁{'成功' if result else '失败'}"
                        }
                    ]
                }
            }
        elif tool_name == "get_session_status":
            result = await self.mcp_server.get_session_status(**arguments)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2, ensure_ascii=False)
                        }
                    ]
                }
            }
        else:
            return self._error_response(request_id, -32601, f"Unknown tool: {tool_name}")
    
    async def _handle_resources_list(self, request_id: Any) -> Dict[str, Any]:
        """处理资源列表请求"""
        resources = [
            {
                "uri": "cursor-bridge://server-status",
                "name": "服务器状态",
                "description": "所有配置服务器的状态信息",
                "mimeType": "application/json"
            },
            {
                "uri": "cursor-bridge://config",
                "name": "配置信息",
                "description": "当前的配置信息",
                "mimeType": "application/json"
            }
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "resources": resources
            }
        }
    
    async def _handle_resources_read(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理资源读取请求"""
        uri = params.get("uri")
        
        if uri == "cursor-bridge://server-status":
            result = await self.mcp_server.get_server_status()
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(result, indent=2, ensure_ascii=False)
                        }
                    ]
                }
            }
        elif uri == "cursor-bridge://config":
            config_dict = {
                "servers": {
                    name: {
                        "type": config.type,
                        "session_name": config.session.name if config.session else None
                    }
                    for name, config in self.mcp_server.config.servers.items()
                }
            }
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(config_dict, indent=2, ensure_ascii=False)
                        }
                    ]
                }
            }
        else:
            return self._error_response(request_id, -32602, f"Unknown resource: {uri}")
    
    def _error_response(self, request_id: Any, code: int, message: str) -> Dict[str, Any]:
        """生成错误响应"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }


async def run_stdio_server(config_path: Optional[str] = None):
    """运行基于stdio的MCP服务器"""
    # 设置日志到文件，避免干扰stdio
    # 重要：MCP协议要求stdout只能用于JSON-RPC消息
    
    # 清除所有现有的处理器
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 只设置文件日志处理器
    file_handler = logging.FileHandler("/tmp/cursor-bridge-mcp.log")
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # 设置所有相关logger只使用文件处理器
    loggers = [
        logging.getLogger("cursor_bridge"),
        logging.getLogger("mcp-stdio"),
        logging.getLogger("mcp-handler"),
        logging.getLogger()
    ]
    
    for logger in loggers:
        logger.handlers.clear()
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    
    logger = logging.getLogger("mcp-stdio")
    logger.info("启动MCP服务器", extra={"config_path": config_path})
    
    # 创建MCP服务器
    mcp_server = MCPServer(config_path)
    handler = SimpleMCPHandler(mcp_server)
    
    # 处理stdio通信
    try:
        while True:
            try:
                # 从stdin读取请求
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    logger.info("stdin关闭，退出服务器")
                    break
                    
                line = line.strip()
                if not line:
                    continue
                
                logger.debug("收到请求", extra={"line": line})
                
                # 解析JSON请求
                try:
                    request = json.loads(line)
                except json.JSONDecodeError as e:
                    logger.error("JSON解析失败", extra={"line": line, "error": str(e)})
                    continue
                
                # 处理请求
                response = await handler.handle_request(request)
                
                # 发送响应到stdout（如果有响应）
                if response is not None:
                    response_line = json.dumps(response, ensure_ascii=False)
                    print(response_line, flush=True)
                    logger.debug("发送响应", extra={"response": response_line})
                
            except Exception as e:
                logger.error("处理请求时发生错误", extra={"error": str(e)})
                # 不要break，继续处理下一个请求
                continue
    
    except KeyboardInterrupt:
        logger.info("收到中断信号")
    except Exception as e:
        logger.error("服务器运行时发生错误", extra={"error": str(e)})
    finally:
        logger.info("MCP服务器关闭")


if __name__ == "__main__":
    import sys
    config_path = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(run_stdio_server(config_path)) 