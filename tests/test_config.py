"""
配置系统测试
"""

import pytest
import tempfile
import yaml
from pathlib import Path

from cursor_bridge.config import ConfigLoader, CursorBridgeConfig


class TestConfigLoader:
    """配置加载器测试"""
    
    def test_load_valid_config(self):
        """测试加载有效配置"""
        config_data = {
            "servers": {
                "test-server": {
                    "type": "direct",
                    "ssh": {
                        "host": "localhost",
                        "username": "test"
                    },
                    "session": {
                        "name": "test-session"
                    }
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name
        
        try:
            loader = ConfigLoader()
            config = loader.load_from_file(config_path)
            
            assert isinstance(config, CursorBridgeConfig)
            assert "test-server" in config.servers
            assert config.servers["test-server"].type == "direct"
            
        finally:
            Path(config_path).unlink()
    
    def test_load_nonexistent_file(self):
        """测试加载不存在的文件"""
        loader = ConfigLoader()
        
        with pytest.raises(FileNotFoundError):
            loader.load_from_file("nonexistent.yaml")
    
    def test_load_invalid_yaml(self):
        """测试加载无效的YAML文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            config_path = f.name
        
        try:
            loader = ConfigLoader()
            
            with pytest.raises(ValueError, match="配置文件格式错误"):
                loader.load_from_file(config_path)
                
        finally:
            Path(config_path).unlink()
    
    def test_validate_config(self):
        """测试配置验证"""
        loader = ConfigLoader()
        
        # 有效配置
        valid_config = CursorBridgeConfig(
            servers={
                "test": {
                    "type": "direct",
                    "ssh": {
                        "host": "localhost",
                        "username": "test"
                    },
                    "session": {
                        "name": "test-session"
                    }
                }
            }
        )
        assert loader.validate_config(valid_config)
        
        # 无效配置：代理模式但缺少代理配置
        invalid_config = CursorBridgeConfig(
            servers={
                "test": {
                    "type": "proxy",
                    "session": {
                        "name": "test-session"
                    }
                }
            }
        )
        assert not loader.validate_config(invalid_config)
    
    def test_get_server_config(self):
        """测试获取服务器配置"""
        config_data = {
            "servers": {
                "test-server": {
                    "type": "direct",
                    "ssh": {
                        "host": "localhost",
                        "username": "test"
                    },
                    "session": {
                        "name": "test-session"
                    }
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name
        
        try:
            loader = ConfigLoader()
            loader.load_from_file(config_path)
            
            server_config = loader.get_server_config("test-server")
            assert server_config is not None
            assert server_config.type == "direct"
            
            # 不存在的服务器
            assert loader.get_server_config("nonexistent") is None
            
        finally:
            Path(config_path).unlink()


class TestCursorBridgeConfig:
    """配置模型测试"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = CursorBridgeConfig(servers={})
        
        assert config.servers == {}
        assert config.security.command_timeout == 300
        assert config.security.max_output_size == 10485760
        assert config.security.max_concurrent_commands == 10
    
    def test_proxy_config(self):
        """测试代理配置"""
        config_data = {
            "servers": {
                "proxy-server": {
                    "type": "proxy",
                    "proxy": {
                        "command": "enterprise-vpn-tool",
                        "target_host": "internal.company.com",
                        "username": "user"
                    },
                    "session": {
                        "name": "proxy-session"
                    }
                }
            }
        }
        
        config = CursorBridgeConfig(**config_data)
        server = config.servers["proxy-server"]
        
        assert server.type == "proxy"
        assert server.proxy is not None
        assert server.proxy.command == "enterprise-vpn-tool"
        assert server.proxy.target_host == "internal.company.com"
        assert server.proxy.target_port == 22  # 默认值
    
    def test_ssh_config(self):
        """测试SSH配置"""
        config_data = {
            "servers": {
                "ssh-server": {
                    "type": "direct",
                    "ssh": {
                        "host": "example.com",
                        "port": 2222,
                        "username": "user",
                        "key_file": "~/.ssh/id_rsa"
                    },
                    "session": {
                        "name": "ssh-session"
                    }
                }
            }
        }
        
        config = CursorBridgeConfig(**config_data)
        server = config.servers["ssh-server"]
        
        assert server.type == "direct"
        assert server.ssh is not None
        assert server.ssh.host == "example.com"
        assert server.ssh.port == 2222
        assert server.ssh.username == "user"
        assert server.ssh.key_file == "~/.ssh/id_rsa"