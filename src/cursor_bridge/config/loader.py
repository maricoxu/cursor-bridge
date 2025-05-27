"""
配置加载器

负责从文件加载和验证配置。
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any

from .models import CursorBridgeConfig


class ConfigLoader:
    """配置加载器"""
    
    @staticmethod
    def load_from_file(config_path: str) -> CursorBridgeConfig:
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
                
            return CursorBridgeConfig(**config_data)
            
        except yaml.YAMLError as e:
            raise ValueError(f"配置文件格式错误: {e}")
        except Exception as e:
            raise ValueError(f"配置加载失败: {e}")
    
    @staticmethod
    def load_from_env() -> CursorBridgeConfig:
        """从环境变量加载配置
        
        Returns:
            配置对象
        """
        config_path = os.getenv('CONFIG_PATH', 'config/cursor_bridge_config.yaml')
        return ConfigLoader.load_from_file(config_path)
    
    @staticmethod
    def validate_config(config: CursorBridgeConfig) -> bool:
        """验证配置有效性
        
        Args:
            config: 配置对象
            
        Returns:
            配置是否有效
        """
        # TODO: 实现配置验证逻辑
        return True