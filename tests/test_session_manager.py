"""
会话管理器测试用例
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch

from cursor_bridge.session import (
    SessionManager, SessionConfig, SessionType, SessionStatus,
    SessionEventType, TmuxBackend
)


class TestSessionManager:
    """会话管理器测试"""
    
    @pytest.fixture
    async def session_manager(self):
        """创建测试用的会话管理器"""
        config = {
            'backend': 'tmux',
            'backend_config': {
                'socket_name': 'test_cursor_bridge',
                'session_prefix': 'test_cb_'
            },
            'auto_cleanup': False,
            'auto_monitor': False
        }
        
        manager = SessionManager(config)
        
        # Mock tmux backend
        with patch.object(manager._backend, '_run_tmux_command') as mock_tmux:
            mock_tmux.return_value = {'exit_code': 0, 'stdout': '', 'stderr': ''}
            yield manager
    
    @pytest.mark.asyncio
    async def test_create_session(self, session_manager):
        """测试创建会话"""
        config = SessionConfig(
            name="test_session",
            server_name="test_server",
            session_type=SessionType.INTERACTIVE
        )
        
        # Mock backend methods
        session_manager._backend.create_session = AsyncMock(return_value=True)
        session_manager._backend.get_session_info = AsyncMock(return_value=Mock(
            name="test_session",
            status=SessionStatus.ACTIVE
        ))
        
        session = await session_manager.create_session(config)
        
        assert session is not None
        assert session.name == "test_session"
        assert session_manager.get_session_count() == 1


@pytest.mark.asyncio
async def test_session_lifecycle():
    """测试完整的会话生命周期"""
    config = {
        'backend': 'tmux',
        'backend_config': {
            'socket_name': 'test_lifecycle',
            'session_prefix': 'lc_'
        },
        'auto_cleanup': False,
        'auto_monitor': False
    }
    
    manager = SessionManager(config)
    
    # Mock所有backend方法
    manager._backend.create_session = AsyncMock(return_value=True)
    manager._backend.destroy_session = AsyncMock(return_value=True)
    manager._backend.get_session_info = AsyncMock(return_value=Mock(
        name="lifecycle_session",
        status=SessionStatus.ACTIVE
    ))
    manager._backend.list_sessions = AsyncMock(return_value=[])
    
    from cursor_bridge.session.models import CommandResult
    mock_result = CommandResult(
        command="pwd",
        exit_code=0,
        stdout="/tmp\n",
        stderr="",
        execution_time=0.05
    )
    manager._backend.execute_command = AsyncMock(return_value=mock_result)
    
    try:
        # 启动管理器
        await manager.start()
        
        # 创建会话
        session_config = SessionConfig(
            name="lifecycle_session",
            server_name="test_server"
        )
        session = await manager.create_session(session_config)
        assert session is not None
        
        # 执行命令
        result = await manager.execute_command("lifecycle_session", "pwd")
        assert result.exit_code == 0
        
        # 销毁会话
        success = await manager.destroy_session("lifecycle_session")
        assert success is True
        
    finally:
        # 停止管理器
        await manager.stop()