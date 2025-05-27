"""配置模块测试"""

import pytest
from cursor_bridge.config.models import ServerConfig, CursorBridgeConfig
from cursor_bridge.config.loader import ConfigLoader


def test_server_config_creation():
    """测试服务器配置创建"""
    config_data = {
        "type": "proxy",
        "proxy": {
            "command": "enterprise-vpn-tool",
            "target_host": "test.com",
            "target_port": 22,
            "username": "test"
        },
        "session": {
            "name": "test-session",
            "working_directory": "/home"
        }
    }
    
    config = ServerConfig(**config_data)
    assert config.type == "proxy"
    assert config.proxy.target_host == "test.com"
    assert config.session.name == "test-session"


def test_cursor_bridge_config_creation():
    """测试完整配置创建"""
    config_data = {
        "servers": {
            "test-server": {
                "type": "proxy",
                "proxy": {
                    "command": "enterprise-vpn-tool",
                    "target_host": "test.com",
                    "target_port": 22,
                    "username": "test"
                },
                "session": {
                    "name": "test-session",
                    "working_directory": "/home"
                }
            }
        }
    }
    
    config = CursorBridgeConfig(**config_data)
    assert "test-server" in config.servers
    assert config.servers["test-server"].type == "proxy"