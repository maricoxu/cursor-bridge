"""
命令执行引擎测试用例
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch

from cursor_bridge.execution import (
    CommandExecutor, ExecutionQueue, CommandHistory,
    ExecutionOptions, ExecutionContext, ExecutionStatus, ExecutionPriority
)
from cursor_bridge.session import SessionManager


class TestExecutionQueue:
    """执行队列测试"""
    
    @pytest.fixture
    def execution_queue(self):
        """创建测试用的执行队列"""
        return ExecutionQueue(max_concurrent=3)
    
    @pytest.mark.asyncio
    async def test_enqueue_dequeue(self, execution_queue):
        """测试入队和出队"""
        from cursor_bridge.execution.models import CommandExecution
        
        # 创建测试执行对象
        context = ExecutionContext(session_name="test")
        options = ExecutionOptions(priority=ExecutionPriority.HIGH)
        execution = CommandExecution(
            context=context,
            command="echo test",
            options=options
        )
        
        # 测试入队
        await execution_queue.enqueue(execution)
        
        # 测试出队
        dequeued = await execution_queue.dequeue()
        assert dequeued is not None
        assert dequeued.command == "echo test"
        assert dequeued.options.priority == ExecutionPriority.HIGH
    
    @pytest.mark.asyncio
    async def test_priority_ordering(self, execution_queue):
        """测试优先级排序"""
        from cursor_bridge.execution.models import CommandExecution
        
        # 创建不同优先级的执行对象
        executions = []
        for priority in [ExecutionPriority.LOW, ExecutionPriority.URGENT, ExecutionPriority.NORMAL]:
            context = ExecutionContext(session_name="test")
            options = ExecutionOptions(priority=priority)
            execution = CommandExecution(
                context=context,
                command=f"echo {priority.name}",
                options=options
            )
            executions.append(execution)
            await execution_queue.enqueue(execution)
        
        # 出队应该按优先级顺序
        first = await execution_queue.dequeue()
        assert first.options.priority == ExecutionPriority.URGENT
        
        second = await execution_queue.dequeue()
        assert second.options.priority == ExecutionPriority.NORMAL
        
        third = await execution_queue.dequeue()
        assert third.options.priority == ExecutionPriority.LOW
    
    def test_queue_stats(self, execution_queue):
        """测试队列统计"""
        stats = execution_queue.get_queue_stats()
        
        assert 'running_count' in stats
        assert 'max_concurrent' in stats
        assert 'queue_sizes' in stats
        assert 'total_queued' in stats
        assert stats['max_concurrent'] == 3


class TestCommandExecutor:
    """命令执行器测试"""
    
    @pytest.fixture
    async def command_executor(self):
        """创建测试用的命令执行器"""
        # Mock SessionManager
        session_manager = Mock(spec=SessionManager)
        session_manager.execute_command = AsyncMock()
        
        config = {
            'max_concurrent_executions': 5
        }
        
        executor = CommandExecutor(session_manager, config)
        yield executor
        
        # 清理
        await executor.stop()
    
    @pytest.mark.asyncio
    async def test_execute_command(self, command_executor):
        """测试执行单个命令"""
        # Mock执行结果
        from cursor_bridge.session.models import CommandResult
        mock_result = CommandResult(
            command="echo hello",
            exit_code=0,
            stdout="hello\n",
            stderr="",
            execution_time=0.1
        )
        command_executor.session_manager.execute_command.return_value = mock_result
        
        # 启动执行器
        await command_executor.start()
        
        # 执行命令
        execution = await command_executor.execute_command(
            session_name="test_session",
            command="echo hello"
        )
        
        assert execution is not None
        assert execution.command == "echo hello"
        assert execution.context.session_name == "test_session"
        assert execution.status == ExecutionStatus.PENDING
    
    @pytest.mark.asyncio
    async def test_execute_batch(self, command_executor):
        """测试批量执行命令"""
        # Mock执行结果
        from cursor_bridge.session.models import CommandResult
        mock_result = CommandResult(
            command="test",
            exit_code=0,
            stdout="output",
            stderr="",
            execution_time=0.1
        )
        command_executor.session_manager.execute_command.return_value = mock_result
        
        # 启动执行器
        await command_executor.start()
        
        # 批量执行
        commands = ["echo 1", "echo 2", "echo 3"]
        batch = await command_executor.execute_batch(
            session_name="test_session",
            commands=commands
        )
        
        assert batch is not None
        assert batch.total_count == 3
        assert len(batch.executions) == 3
        
        # 检查每个执行对象
        for i, execution in enumerate(batch.executions):
            assert execution.command == commands[i]
            assert execution.context.session_name == "test_session"
    
    def test_get_stats(self, command_executor):
        """测试获取统计信息"""
        stats = command_executor.get_stats()
        
        assert 'total_executions' in stats
        assert 'successful_executions' in stats
        assert 'failed_executions' in stats
        assert 'average_execution_time' in stats
        assert 'queue_stats' in stats


class TestCommandHistory:
    """命令历史测试"""
    
    @pytest.fixture
    def command_history(self, tmp_path):
        """创建测试用的命令历史管理器"""
        db_path = tmp_path / "test_history.db"
        return CommandHistory(str(db_path))
    
    @pytest.mark.asyncio
    async def test_save_and_get_execution(self, command_history):
        """测试保存和获取执行记录"""
        from cursor_bridge.execution.models import CommandExecution
        
        # 创建测试执行记录
        context = ExecutionContext(session_name="test_session")
        options = ExecutionOptions()
        execution = CommandExecution(
            context=context,
            command="echo test",
            options=options,
            status=ExecutionStatus.COMPLETED,
            exit_code=0,
            stdout="test output"
        )
        execution.started_at = time.time()
        execution.completed_at = time.time() + 1
        
        # 保存记录
        await command_history.save_execution(execution)
        
        # 获取记录
        saved_record = await command_history.get_execution(execution.context.execution_id)
        
        assert saved_record is not None
        assert saved_record['command'] == "echo test"
        assert saved_record['session_name'] == "test_session"
        assert saved_record['status'] == ExecutionStatus.COMPLETED.value
        assert saved_record['exit_code'] == 0
    
    @pytest.mark.asyncio
    async def test_query_executions(self, command_history):
        """测试查询执行记录"""
        from cursor_bridge.execution.models import CommandExecution
        
        # 创建多个测试记录
        for i in range(5):
            context = ExecutionContext(session_name=f"session_{i}")
            options = ExecutionOptions()
            execution = CommandExecution(
                context=context,
                command=f"echo test_{i}",
                options=options,
                status=ExecutionStatus.COMPLETED
            )
            await command_history.save_execution(execution)
        
        # 查询所有记录
        all_records = await command_history.query_executions(limit=10)
        assert len(all_records) == 5
        
        # 按会话名称查询
        session_records = await command_history.query_executions(
            session_name="session_0"
        )
        assert len(session_records) == 1
        assert session_records[0]['session_name'] == "session_0"
    
    @pytest.mark.asyncio
    async def test_get_execution_stats(self, command_history):
        """测试获取执行统计"""
        from cursor_bridge.execution.models import CommandExecution
        
        # 创建测试记录
        for i in range(10):
            context = ExecutionContext(session_name="test_session")
            options = ExecutionOptions()
            execution = CommandExecution(
                context=context,
                command=f"echo test_{i}",
                options=options,
                status=ExecutionStatus.COMPLETED if i < 8 else ExecutionStatus.FAILED,
                exit_code=0 if i < 8 else 1
            )
            execution.started_at = time.time()
            execution.completed_at = time.time() + 0.1
            await command_history.save_execution(execution)
        
        # 获取统计信息
        stats = await command_history.get_execution_stats()
        
        assert stats.total_executions == 10
        assert stats.successful_executions == 8
        assert stats.failed_executions == 2
        assert stats.success_rate == 0.8
    
    @pytest.mark.asyncio
    async def test_command_suggestions(self, command_history):
        """测试命令建议"""
        from cursor_bridge.execution.models import CommandExecution
        
        # 创建测试记录
        commands = ["git status", "git add .", "git commit", "ls -la", "git push"]
        for cmd in commands:
            context = ExecutionContext(session_name="test_session")
            options = ExecutionOptions()
            execution = CommandExecution(
                context=context,
                command=cmd,
                options=options
            )
            await command_history.save_execution(execution)
        
        # 获取git命令建议
        suggestions = await command_history.get_command_suggestions(
            session_name="test_session",
            prefix="git"
        )
        
        assert len(suggestions) == 4
        assert all(cmd.startswith("git") for cmd in suggestions)


@pytest.mark.asyncio
async def test_execution_lifecycle():
    """测试完整的执行生命周期"""
    # Mock SessionManager
    session_manager = Mock(spec=SessionManager)
    
    from cursor_bridge.session.models import CommandResult
    mock_result = CommandResult(
        command="echo lifecycle",
        exit_code=0,
        stdout="lifecycle test",
        stderr="",
        execution_time=0.1
    )
    session_manager.execute_command = AsyncMock(return_value=mock_result)
    
    # 创建执行器
    config = {'max_concurrent_executions': 2}
    executor = CommandExecutor(session_manager, config)
    
    try:
        # 启动执行器
        await executor.start()
        
        # 执行命令
        execution = await executor.execute_command(
            session_name="lifecycle_session",
            command="echo lifecycle"
        )
        
        # 等待执行完成
        await asyncio.sleep(0.5)
        
        # 验证执行结果
        final_execution = executor.get_execution(execution.context.execution_id)
        assert final_execution is not None
        assert final_execution.status in [ExecutionStatus.COMPLETED, ExecutionStatus.RUNNING]
        
    finally:
        # 停止执行器
        await executor.stop()