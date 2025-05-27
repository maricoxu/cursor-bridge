"""
配置加载器

负责从文件加载和验证配置。
"""

import os
import yaml
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .models import CursorBridgeConfig

logger = logging.getLogger(__name__)


class ConfigFileHandler(FileSystemEventHandler):
    """配置文件变更监听器"""
    
    def __init__(self, config_path: str, reload_callback: Callable):
        self.config_path = Path(config_path).resolve()
        self.reload_callback = reload_callback
        
    def on_modified(self, event):
        if not event.is_directory and Path(event.src_path).resolve() == self.config_path:
            logger.info(f"配置文件已修改: {event.src_path}")
            try:
                self.reload_callback()
            except Exception as e:
                logger.error(f"配置重载失败: {e}")


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self):
        self._config: Optional[CursorBridgeConfig] = None
        self._config_path: Optional[str] = None
        self._observer: Optional[Observer] = None
        self._reload_callbacks: list[Callable] = []
    
    def load_from_file(self, config_path: str) -> CursorBridgeConfig:
        """从文件加载配置
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            解析后的配置对象
            
        Raises:
            FileNotFoundError: 配置文件不存在
            ValueError: 配置格式错误
        """
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
            
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                
            if config_data is None:
                config_data = {}
                
            config = CursorBridgeConfig(**config_data)
            
            # 验证配置
            if not self.validate_config(config):
                raise ValueError("配置验证失败")
                
            self._config = config
            self._config_path = str(config_file.resolve())
            
            logger.info(f"配置加载成功: {config_path}")
            return config
            
        except yaml.YAMLError as e:
            raise ValueError(f"配置文件格式错误: {e}")
        except Exception as e:
            raise ValueError(f"配置加载失败: {e}")
    
    def load_from_env(self) -> CursorBridgeConfig:
        """从环境变量加载配置
        
        Returns:
            配置对象
        """
        config_path = os.getenv('CURSOR_BRIDGE_CONFIG', 'config/cursor_bridge_config.yaml')
        return self.load_from_file(config_path)
    
    def validate_config(self, config: CursorBridgeConfig) -> bool:
        """验证配置有效性
        
        Args:
            config: 配置对象
            
        Returns:
            配置是否有效
        """
        try:
            # 验证服务器配置
            if not config.servers:
                logger.warning("未配置任何服务器")
                return False
                
            for server_name, server_config in config.servers.items():
                if server_config.type == "proxy" and not server_config.proxy:
                    logger.error(f"服务器 {server_name} 配置为代理模式但缺少代理配置")
                    return False
                    
                if server_config.type == "direct" and not server_config.ssh:
                    logger.error(f"服务器 {server_name} 配置为直连模式但缺少SSH配置")
                    return False
                    
            # 验证安全配置
            if config.security.command_timeout <= 0:
                logger.error("命令超时时间必须大于0")
                return False
                
            if config.security.max_output_size <= 0:
                logger.error("最大输出大小必须大于0")
                return False
                
            logger.info("配置验证通过")
            return True
            
        except Exception as e:
            logger.error(f"配置验证失败: {e}")
            return False
    
    def enable_hot_reload(self, reload_callback: Optional[Callable] = None):
        """启用配置热重载
        
        Args:
            reload_callback: 配置重载时的回调函数
        """
        if not self._config_path:
            logger.warning("未加载配置文件，无法启用热重载")
            return
            
        if reload_callback:
            self._reload_callbacks.append(reload_callback)
            
        config_dir = Path(self._config_path).parent
        
        def reload_config():
            try:
                old_config = self._config
                new_config = self.load_from_file(self._config_path)
                
                # 通知所有回调函数
                for callback in self._reload_callbacks:
                    try:
                        callback(old_config, new_config)
                    except Exception as e:
                        logger.error(f"配置重载回调失败: {e}")
                        
                logger.info("配置热重载成功")
                
            except Exception as e:
                logger.error(f"配置热重载失败: {e}")
        
        handler = ConfigFileHandler(self._config_path, reload_config)
        self._observer = Observer()
        self._observer.schedule(handler, str(config_dir), recursive=False)
        self._observer.start()
        
        logger.info(f"配置热重载已启用，监听目录: {config_dir}")
    
    def disable_hot_reload(self):
        """禁用配置热重载"""
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None
            logger.info("配置热重载已禁用")
    
    @property
    def config(self) -> Optional[CursorBridgeConfig]:
        """获取当前配置"""
        return self._config
    
    def get_server_config(self, server_name: str) -> Optional[Any]:
        """获取指定服务器配置
        
        Args:
            server_name: 服务器名称
            
        Returns:
            服务器配置或None
        """
        if not self._config:
            return None
            
        return self._config.servers.get(server_name)