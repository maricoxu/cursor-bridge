"""
会话管理器

负责管理tmux会话。
"""

from typing import Dict, Optional, Any, List
import asyncio
import logging

logger = logging.getLogger(__name__)


class Session:
    """会话对象"""
    
    def __init__(self, name: str, server_name: str):
        self.name = name
        self.server_name = server_name
        self._active = False
        
    async def create(self) -> bool:
        """创建会话"""
        # TODO: 实现会话创建逻辑
        logger.info(f"创建会话: {self.name} on {self.server_name}")
        self._active = True
        return True
        
    async def destroy(self) -> None:
        """销毁会话"""
        # TODO: 实现会话销毁逻辑
        logger.info(f"销毁会话: {self.name}")
        self._active = False
        
    @property
    def is_active(self) -> bool:
        """检查会话是否活跃"""
        return self._active


class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        
    async def create_session(self, name: str, server_name: str) -> Session:
        """创建会话
        
        Args:
            name: 会话名称
            server_name: 服务器名称
            
        Returns:
            会话对象
        """
        if name in self._sessions:
            return self._sessions[name]
            
        session = Session(name, server_name)
        await session.create()
        self._sessions[name] = session
        
        return session
    
    async def get_session(self, name: str) -> Optional[Session]:
        """获取会话
        
        Args:
            name: 会话名称
            
        Returns:
            会话对象或None
        """
        return self._sessions.get(name)
    
    async def destroy_session(self, name: str) -> None:
        """销毁会话
        
        Args:
            name: 会话名称
        """
        if name in self._sessions:
            await self._sessions[name].destroy()
            del self._sessions[name]
    
    async def destroy_all_sessions(self) -> None:
        """销毁所有会话"""
        for name in list(self._sessions.keys()):
            await self.destroy_session(name)
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """列出所有会话
        
        Returns:
            会话信息列表
        """
        return [
            {
                "name": session.name,
                "server": session.server_name,
                "active": session.is_active
            }
            for session in self._sessions.values()
        ]