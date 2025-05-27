#!/usr/bin/env python3
"""
基本功能测试脚本
"""

import asyncio
import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cursor_bridge.server import create_server
from cursor_bridge.utils import setup_logging


async def test_server():
    """测试服务器基本功能"""
    print("🚀 开始测试Cursor Bridge服务器...")
    
    # 设置日志
    setup_logging(level="INFO")
    
    try:
        # 创建服务器
        print("📦 创建服务器实例...")
        server = await create_server()
        print(f"✅ 服务器创建成功，配置了 {len(server.config.servers)} 个服务器")
        
        # 测试ping
        print("🏓 测试ping功能...")
        ping_result = await server.ping()
        print(f"✅ Ping成功: {ping_result['status']}")
        
        # 测试健康检查
        print("🏥 测试健康检查...")
        health = await server.get_health()
        print(f"✅ 健康检查成功: {health['status']}")
        print(f"   运行时间: {health['uptime']:.2f}秒")
        print(f"   检查项: {len(health['checks'])}个")
        
        # 测试配置访问
        print("⚙️  测试配置访问...")
        for server_name in server.config.servers:
            server_config = server.config_loader.get_server_config(server_name)
            print(f"   服务器 {server_name}: {server_config.type}")
        
        print("🎉 所有基本功能测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_server()) 