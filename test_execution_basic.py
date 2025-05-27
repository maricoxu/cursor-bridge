#!/usr/bin/env python3
"""
基础执行模块测试
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cursor_bridge.execution.models import (
    ExecutionStatus, ExecutionPriority, ExecutionOptions, 
    ExecutionContext, CommandExecution
)

def test_execution_models():
    """测试执行模型"""
    print("🧪 测试执行模型...")
    
    # 测试执行选项
    options = ExecutionOptions(
        timeout=60,
        priority=ExecutionPriority.HIGH,
        retry_count=3
    )
    assert options.timeout == 60
    assert options.priority == ExecutionPriority.HIGH
    assert options.retry_count == 3
    print("✅ ExecutionOptions 测试通过")
    
    # 测试执行上下文
    context = ExecutionContext(session_name="test_session")
    assert context.session_name == "test_session"
    assert context.execution_id is not None
    print("✅ ExecutionContext 测试通过")
    
    # 测试命令执行
    execution = CommandExecution(
        context=context,
        command="echo hello",
        options=options
    )
    assert execution.command == "echo hello"
    assert execution.status == ExecutionStatus.PENDING
    assert not execution.is_running
    assert not execution.is_completed
    print("✅ CommandExecution 测试通过")
    
    # 测试状态转换
    execution.status = ExecutionStatus.RUNNING
    assert execution.is_running
    assert not execution.is_completed
    
    execution.status = ExecutionStatus.COMPLETED
    execution.exit_code = 0
    assert not execution.is_running
    assert execution.is_completed
    assert execution.is_successful
    print("✅ 状态转换测试通过")
    
    # 测试字典转换
    execution_dict = execution.to_dict()
    assert execution_dict['command'] == "echo hello"
    assert execution_dict['status'] == ExecutionStatus.COMPLETED.value
    assert execution_dict['is_successful'] is True
    print("✅ 字典转换测试通过")

def test_priority_ordering():
    """测试优先级排序"""
    print("\n🧪 测试优先级排序...")
    
    priorities = [ExecutionPriority.LOW, ExecutionPriority.URGENT, ExecutionPriority.NORMAL, ExecutionPriority.HIGH]
    sorted_priorities = sorted(priorities, key=lambda p: p.value, reverse=True)
    
    expected_order = [ExecutionPriority.URGENT, ExecutionPriority.HIGH, ExecutionPriority.NORMAL, ExecutionPriority.LOW]
    assert sorted_priorities == expected_order
    print("✅ 优先级排序测试通过")

def main():
    """主测试函数"""
    print("🚀 开始阶段4命令执行引擎基础测试\n")
    
    try:
        test_execution_models()
        test_priority_ordering()
        
        print("\n🎉 所有基础测试通过！")
        print("\n📊 测试总结:")
        print("- ✅ 执行数据模型")
        print("- ✅ 状态管理")
        print("- ✅ 优先级排序")
        print("- ✅ 数据序列化")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)