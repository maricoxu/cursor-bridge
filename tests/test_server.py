"""
服务器核心功能测试
"""

import pytest
import asyncio
import tempfile
import yaml
from pathlib import Path
import os

from cursor_bridge.server import CursorBridgeServer, HealthChecker, create_server


class TestHealthChecker:
    """健康检查器测试"""
    
    def test_initial_status(self):
        """测试初始状态"""
        checker = HealthChecker()
        assert checker.status == "starting"
        assert checker.checks == {}
    
    def test_set_status(self):
        """测试设置状态"""
        checker = HealthChecker()
        checker.set_status("healthy")
        assert checker.status == "healthy"
    
    def test_add_check(self):
        """测试添加检查项"""
        checker = HealthChecker()
        checker.add_check("test", "ok", {"detail": "value"})
        
        assert "test" in checker.checks
        assert checker.checks["test"]["status"] == "ok"
        assert checker.checks["test"]["details"]["detail"] == "value"
    
    @pytest.mark.asyncio
    async def test_check_health(self):
        """测试健康检查"""
        checker = HealthChecker()
        checker.set_status("healthy")
        checker.add_check("component1", "ok")
        
        health = await checker.check_health()
        
        assert health["status"] == "healthy"
        assert "uptime" in health
        assert "timestamp" in health
        assert "component1" in health["checks"]


class TestCursorBridgeServer:
    """Cursor Bridge服务器测试"""
    
    def create_test_config(self):
        """创建测试配置文件"""
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
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        yaml.dump(config_data, temp_file)
        temp_file.close()
        
        return temp_file.name
    
    def test_server_creation_with_config(self):
        """测试使用配置文件创建服务器"""
        config_path = self.create_test_config()
        
        try:
            server = CursorBridgeServer(config_path)
            assert server.config is not None
            assert "test-server" in server.config.servers
            assert not server.is_running
            
        finally:
            Path(config_path).unlink()
    
    def test_server_creation_without_config(self):
        """测试不使用配置文件创建服务器"""
        # 设置一个不存在的配置文件路径
        old_env = os.environ.get('CURSOR_BRIDGE_CONFIG')
        os.environ['CURSOR_BRIDGE_CONFIG'] = '/nonexistent/config.yaml'
        
        try:
            server = CursorBridgeServer()
            assert server.config is not None
            assert server.config.servers == {}
            assert not server.is_running
        finally:
            # 恢复环境变量
            if old_env is not None:
                os.environ['CURSOR_BRIDGE_CONFIG'] = old_env
            elif 'CURSOR_BRIDGE_CONFIG' in os.environ:
                del os.environ['CURSOR_BRIDGE_CONFIG']
    
    @pytest.mark.asyncio
    async def test_ping(self):
        """测试ping功能"""
        server = CursorBridgeServer()
        result = await server.ping()
        
        assert result["status"] == "ok"
        assert result["service"] == "cursor-bridge"
        assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """测试健康检查"""
        server = CursorBridgeServer()
        health = await server.get_health()
        
        assert "status" in health
        assert "uptime" in health
        assert "timestamp" in health
        assert "checks" in health
    
    @pytest.mark.asyncio
    async def test_server_lifecycle(self):
        """测试服务器生命周期"""
        config_path = self.create_test_config()
        
        try:
            server = CursorBridgeServer(config_path)
            
            # 初始状态
            assert not server.is_running
            assert server.health_checker.status == "starting"
            
            # 启动服务器（在后台任务中）
            start_task = asyncio.create_task(server.start())
            
            # 等待一小段时间让服务器启动
            await asyncio.sleep(0.1)
            
            # 检查运行状态
            assert server.is_running
            assert server.health_checker.status == "healthy"
            
            # 停止服务器
            await server.stop()
            
            # 等待启动任务完成
            await start_task
            
            # 检查停止状态
            assert not server.is_running
            assert server.health_checker.status == "stopped"
            
        finally:
            Path(config_path).unlink()
    
    @pytest.mark.asyncio
    async def test_config_reload(self):
        """测试配置重载"""
        config_path = self.create_test_config()
        
        try:
            server = CursorBridgeServer(config_path)
            original_servers = len(server.config.servers)
            
            # 修改配置文件
            new_config_data = {
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
                    },
                    "new-server": {
                        "type": "direct",
                        "ssh": {
                            "host": "example.com",
                            "username": "user"
                        },
                        "session": {
                            "name": "new-session"
                        }
                    }
                }
            }
            
            with open(config_path, 'w') as f:
                yaml.dump(new_config_data, f)
            
            # 手动触发配置重载
            server._on_config_reload(server.config, server.config_loader.load_from_file(config_path))
            
            # 验证配置已更新
            assert len(server.config.servers) == 2
            assert "new-server" in server.config.servers
            
        finally:
            Path(config_path).unlink()


@pytest.mark.asyncio
async def test_create_server():
    """测试服务器创建函数"""
    server = await create_server()
    assert isinstance(server, CursorBridgeServer)
    assert server.config is not None 