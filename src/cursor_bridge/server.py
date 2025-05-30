"""
Cursor Bridge MCP服务器主入口

这是MCP服务器的主要实现文件。
"""

import asyncio
import signal
import time
from typing import Any, Dict, List, Optional
from pathlib import Path

from .config import ConfigLoader, CursorBridgeConfig
from .utils import setup_logging, get_logger, LoggerMixin
from .connection import ConnectionManager


class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self.start_time = time.time()
        self.status = "starting"
        self.checks = {}
        
    async def check_health(self) -> Dict[str, Any]:
        """执行健康检查
        
        Returns:
            健康状态信息
        """
        uptime = time.time() - self.start_time
        
        health_info = {
            "status": self.status,
            "uptime": uptime,
            "timestamp": time.time(),
            "checks": self.checks.copy()
        }
        
        return health_info
    
    def set_status(self, status: str):
        """设置服务状态"""
        self.status = status
        
    def add_check(self, name: str, status: str, details: Optional[Dict] = None):
        """添加检查项"""
        self.checks[name] = {
            "status": status,
            "timestamp": time.time(),
            "details": details or {}
        }


class CursorBridgeServer(LoggerMixin):
    """Cursor Bridge MCP服务器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化服务器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_loader = ConfigLoader()
        self.config: Optional[CursorBridgeConfig] = None
        self.health_checker = HealthChecker()
        self.connection_manager = ConnectionManager()
        self._running = False
        self._shutdown_event = asyncio.Event()
        
        # 加载配置
        if config_path:
            self.config = self.config_loader.load_from_file(config_path)
        else:
            try:
                self.config = self.config_loader.load_from_env()
            except FileNotFoundError:
                self.logger.warning("未找到配置文件，使用默认配置")
                self.config = CursorBridgeConfig(servers={})
        
        # 设置配置重载回调
        self.config_loader.enable_hot_reload(self._on_config_reload)
        
    def _on_config_reload(self, old_config: CursorBridgeConfig, new_config: CursorBridgeConfig):
        """配置重载回调"""
        self.logger.info("配置已重载", 
                        old_servers=len(old_config.servers),
                        new_servers=len(new_config.servers))
        self.config = new_config
        
    async def start(self) -> None:
        """启动服务器"""
        self.logger.info("启动Cursor Bridge服务器...")
        
        try:
            # 设置信号处理
            self._setup_signal_handlers()
            
            # 更新健康状态
            self.health_checker.set_status("starting")
            self.health_checker.add_check("config", "ok", {"servers": len(self.config.servers)})
            
            # 初始化各个组件
            await self._initialize_components()
            
            # 标记为运行状态
            self._running = True
            self.health_checker.set_status("healthy")
            
            self.logger.info("Cursor Bridge服务器启动成功", 
                           servers=len(self.config.servers))
            
            # 等待关闭信号
            await self._shutdown_event.wait()
            
        except Exception as e:
            self.logger.error("服务器启动失败", error=str(e))
            self.health_checker.set_status("error")
            self.health_checker.add_check("startup", "failed", {"error": str(e)})
            raise
        
    async def stop(self) -> None:
        """停止服务器"""
        self.logger.info("停止Cursor Bridge服务器...")
        
        self.health_checker.set_status("stopping")
        self._running = False
        
        # 清理资源
        await self._cleanup_components()
        
        # 禁用配置热重载
        self.config_loader.disable_hot_reload()
        
        self.health_checker.set_status("stopped")
        self.logger.info("Cursor Bridge服务器已停止")
        
        # 触发关闭事件
        self._shutdown_event.set()
        
    async def _initialize_components(self):
        """初始化各个组件"""
        self.logger.info("初始化组件...")
        
        # 初始化连接管理器
        await self.connection_manager.start()
        self.health_checker.add_check("connection_manager", "ok")
        
        # TODO: 初始化会话管理器
        self.health_checker.add_check("session_manager", "ok")
        
        # TODO: 初始化命令执行器
        self.health_checker.add_check("command_executor", "ok")
        
        self.logger.info("组件初始化完成")
        
    async def _cleanup_components(self):
        """清理组件"""
        self.logger.info("清理组件...")
        
        # 清理连接管理器
        await self.connection_manager.stop()
        
        # TODO: 清理其他组件
        
        self.logger.info("组件清理完成")
        
    def _setup_signal_handlers(self):
        """设置信号处理器"""
        def signal_handler(signum, frame):
            self.logger.info("收到关闭信号", signal=signum)
            asyncio.create_task(self.stop())
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    @property
    def is_running(self) -> bool:
        """检查服务器是否运行中"""
        return self._running
        
    async def get_health(self) -> Dict[str, Any]:
        """获取健康状态"""
        return await self.health_checker.check_health()
        
    async def ping(self) -> Dict[str, Any]:
        """Ping检查"""
        return {
            "status": "ok",
            "timestamp": time.time(),
            "service": "cursor-bridge"
        }


async def create_server(config_path: Optional[str] = None) -> CursorBridgeServer:
    """创建服务器实例
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        服务器实例
    """
    return CursorBridgeServer(config_path)


async def main():
    """主函数"""
    # 设置日志
    setup_logging(level="INFO", service_name="cursor-bridge")
    logger = get_logger("main")
    
    logger.info("Cursor Bridge服务器启动中...")
    
    try:
        # 创建并启动服务器
        server = await create_server()
        await server.start()
        
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭...")
    except Exception as e:
        logger.error("服务器运行失败", error=str(e))
        raise
    finally:
        logger.info("服务器已关闭")
    

if __name__ == "__main__":
    asyncio.run(main())