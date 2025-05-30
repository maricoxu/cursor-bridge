"""
本地tmux会话后端

通过tmux命令与本地已建立的tmux会话交互，这些会话内部已经连接到远程服务器。
"""

import asyncio
import subprocess
import time
from typing import Dict, Any, Optional, List
import logging
import re

logger = logging.getLogger(__name__)


class TmuxSession:
    """本地tmux会话控制器"""
    
    def __init__(self, session_name: str, window_name: str = "main"):
        """初始化tmux会话控制器
        
        Args:
            session_name: tmux会话名称
            window_name: 窗口名称
        """
        self.session_name = session_name
        self.window_name = window_name
        self.target = f"{session_name}:{window_name}"
        
    async def check_session_exists(self) -> bool:
        """检查tmux会话是否存在"""
        try:
            cmd = ["tmux", "has-session", "-t", self.session_name]
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.wait()
            return result.returncode == 0
        except Exception as e:
            logger.error(f"检查会话失败: {e}")
            return False
    
    async def send_command(self, command: str, wait_time: float = 1.0) -> Dict[str, Any]:
        """发送命令到tmux会话
        
        Args:
            command: 要执行的命令
            wait_time: 等待命令执行完成的时间（秒）
            
        Returns:
            命令执行结果
        """
        start_time = time.time()
        
        try:
            # 1. 检查会话是否存在
            if not await self.check_session_exists():
                return {
                    "stdout": "",
                    "stderr": f"tmux会话 '{self.session_name}' 不存在",
                    "exit_code": 1,
                    "execution_time": 0,
                    "command": command
                }
            
            # 2. 发送命令
            send_cmd = ["tmux", "send-keys", "-t", self.target, command, "Enter"]
            logger.info(f"发送命令: {' '.join(send_cmd)}")
            
            result = await asyncio.create_subprocess_exec(
                *send_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.wait()
            
            if result.returncode != 0:
                stderr_data = await result.stderr.read()
                return {
                    "stdout": "",
                    "stderr": stderr_data.decode('utf-8', errors='ignore'),
                    "exit_code": result.returncode,
                    "execution_time": time.time() - start_time,
                    "command": command
                }
            
            # 3. 等待命令执行完成
            await asyncio.sleep(wait_time)
            
            # 4. 捕获最近的输出
            capture_result = await self.capture_output(lines=20)  # 只捕获最近20行
            filtered_output = self._extract_recent_output(capture_result, command)
            
            execution_time = time.time() - start_time
            
            return {
                "stdout": filtered_output,
                "stderr": "",
                "exit_code": 0,  # tmux命令成功，具体命令的退出码在输出中
                "execution_time": execution_time,
                "command": command
            }
            
        except Exception as e:
            logger.error(f"执行命令失败: {e}")
            return {
                "stdout": "",
                "stderr": str(e),
                "exit_code": 1,
                "execution_time": time.time() - start_time,
                "command": command
            }
    
    def _extract_recent_output(self, full_output: str, command: str) -> str:
        """提取最近的命令输出"""
        lines = full_output.split('\n')
        
        # 找到最后一次命令执行的位置
        command_index = -1
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i].strip()
            if command in line:
                command_index = i
                break
        
        if command_index == -1:
            # 如果没找到命令，返回最后几行（排除空行）
            result_lines = []
            for line in lines[-10:]:
                if line.strip():
                    result_lines.append(line)
            return '\n'.join(result_lines)
        
        # 返回命令执行后的输出
        result_lines = []
        for i in range(command_index + 1, len(lines)):
            line = lines[i]
            stripped = line.strip()
            if stripped:  # 只保留非空行
                result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    async def capture_output(self, lines: int = 100) -> str:
        """捕获tmux面板输出
        
        Args:
            lines: 捕获的行数
            
        Returns:
            输出内容
        """
        try:
            # 使用 -p 参数直接输出，-S 指定开始行数
            cmd = ["tmux", "capture-pane", "-t", self.target, "-p", "-S", f"-{lines}"]
            logger.debug(f"捕获输出: {' '.join(cmd)}")
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout_data, stderr_data = await result.communicate()
            
            if result.returncode != 0:
                logger.error(f"捕获输出失败: {stderr_data.decode('utf-8', errors='ignore')}")
                return ""
            
            output = stdout_data.decode('utf-8', errors='ignore')
            
            # 清理输出：移除ANSI转义码
            output = self._clean_ansi_codes(output)
            
            return output
            
        except Exception as e:
            logger.error(f"捕获输出异常: {e}")
            return ""
    
    def _clean_ansi_codes(self, text: str) -> str:
        """清理ANSI转义码"""
        # 移除ANSI转义序列
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    async def get_session_info(self) -> Dict[str, Any]:
        """获取会话信息"""
        try:
            # 获取会话列表
            cmd = ["tmux", "list-sessions", "-F", "#{session_name},#{session_created},#{session_attached}"]
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout_data, stderr_data = await result.communicate()
            
            if result.returncode != 0:
                return {"exists": False, "error": stderr_data.decode('utf-8', errors='ignore')}
            
            sessions = stdout_data.decode('utf-8', errors='ignore').strip().split('\n')
            
            for session_line in sessions:
                if not session_line:
                    continue
                    
                parts = session_line.split(',')
                if len(parts) >= 3 and parts[0] == self.session_name:
                    return {
                        "exists": True,
                        "name": parts[0],
                        "created": parts[1],
                        "attached": parts[2] == "1"
                    }
            
            return {"exists": False}
            
        except Exception as e:
            logger.error(f"获取会话信息失败: {e}")
            return {"exists": False, "error": str(e)}


class TmuxBackend:
    """tmux后端管理器"""
    
    def __init__(self):
        self.sessions: Dict[str, TmuxSession] = {}
        
    def get_session(self, session_name: str, window_name: str = "main") -> TmuxSession:
        """获取或创建tmux会话控制器
        
        Args:
            session_name: 会话名称
            window_name: 窗口名称
            
        Returns:
            tmux会话控制器
        """
        key = f"{session_name}:{window_name}"
        
        if key not in self.sessions:
            self.sessions[key] = TmuxSession(session_name, window_name)
            
        return self.sessions[key]
    
    async def list_all_sessions(self) -> List[Dict[str, Any]]:
        """列出所有tmux会话"""
        try:
            cmd = ["tmux", "list-sessions", "-F", "#{session_name},#{session_created},#{session_attached}"]
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout_data, stderr_data = await result.communicate()
            
            if result.returncode != 0:
                logger.error(f"列出会话失败: {stderr_data.decode('utf-8', errors='ignore')}")
                return []
            
            sessions = []
            lines = stdout_data.decode('utf-8', errors='ignore').strip().split('\n')
            
            for line in lines:
                if not line:
                    continue
                    
                parts = line.split(',')
                if len(parts) >= 3:
                    sessions.append({
                        "name": parts[0],
                        "created": parts[1],
                        "attached": parts[2] == "1"
                    })
            
            return sessions
            
        except Exception as e:
            logger.error(f"列出会话异常: {e}")
            return []


# 全局tmux后端实例
tmux_backend = TmuxBackend()
