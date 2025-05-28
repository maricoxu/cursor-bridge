"""
命令行接口

提供cursor-bridge的命令行工具。
"""

import asyncio
import click
import json
from pathlib import Path
from typing import Optional

from .server import create_server, CursorBridgeServer
from .utils import setup_logging


@click.group()
@click.option('--config', '-c', type=click.Path(exists=True), help='配置文件路径')
@click.option('--log-level', default='INFO', help='日志级别')
@click.option('--log-file', type=click.Path(), help='日志文件路径')
@click.pass_context
def cli(ctx, config, log_level, log_file):
    """Cursor Bridge - 企业远程开发解决方案"""
    ctx.ensure_object(dict)
    ctx.obj['config'] = config
    ctx.obj['log_level'] = log_level
    ctx.obj['log_file'] = log_file
    
    # 设置日志
    setup_logging(
        level=log_level,
        log_file=log_file,
        service_name="cursor-bridge"
    )


@cli.command()
@click.pass_context
def start(ctx):
    """启动Cursor Bridge服务器"""
    async def _start():
        config_path = ctx.obj.get('config')
        server = await create_server(config_path)
        
        click.echo("🚀 启动Cursor Bridge服务器...")
        click.echo(f"📦 配置了 {len(server.config.servers)} 个服务器")
        
        try:
            await server.start()
        except KeyboardInterrupt:
            click.echo("\n⏹️  收到中断信号，正在关闭服务器...")
            await server.stop()
        except Exception as e:
            click.echo(f"❌ 服务器启动失败: {e}")
            raise
    
    asyncio.run(_start())


@cli.command()
@click.pass_context
def ping(ctx):
    """测试服务器连通性"""
    async def _ping():
        config_path = ctx.obj.get('config')
        server = await create_server(config_path)
        
        result = await server.ping()
        click.echo(f"🏓 Ping结果: {json.dumps(result, indent=2)}")
    
    asyncio.run(_ping())


@cli.command()
@click.pass_context
def health(ctx):
    """检查服务器健康状态"""
    async def _health():
        config_path = ctx.obj.get('config')
        server = await create_server(config_path)
        
        health_info = await server.get_health()
        click.echo(f"🏥 健康状态: {json.dumps(health_info, indent=2)}")
    
    asyncio.run(_health())


@cli.command()
@click.pass_context
def config(ctx):
    """显示当前配置"""
    async def _config():
        config_path = ctx.obj.get('config')
        server = await create_server(config_path)
        
        click.echo("⚙️  当前配置:")
        click.echo(f"   配置文件: {server.config_loader._config_path or '默认配置'}")
        click.echo(f"   服务器数量: {len(server.config.servers)}")
        
        for name, server_config in server.config.servers.items():
            click.echo(f"   📡 {name}: {server_config.type}")
            if server_config.type == "proxy" and server_config.proxy:
                click.echo(f"      代理: {server_config.proxy.command}")
                click.echo(f"      目标: {server_config.proxy.target_host}:{server_config.proxy.target_port}")
            elif server_config.type == "direct" and server_config.ssh:
                click.echo(f"      SSH: {server_config.ssh.host}:{server_config.ssh.port}")
                click.echo(f"      用户: {server_config.ssh.username}")
    
    asyncio.run(_config())


@cli.command()
@click.option('--output', '-o', type=click.Path(), help='输出文件路径')
def init_config(output):
    """生成示例配置文件"""
    config_content = """# Cursor Bridge 配置文件

# 服务器配置
servers:
  # 企业代理连接示例
  enterprise-dev:
    type: proxy
    proxy:
      command: "enterprise-vpn-tool"
      target_host: "internal-server.company.com"
      target_port: 22
      username: "developer"
      timeout: 30
      extra_args: []
    session:
      name: "enterprise-dev-session"
      working_directory: "/home/developer"
      environment:
        TERM: "xterm-256color"
        LANG: "en_US.UTF-8"
      shell: "/bin/bash"

  # 直连SSH示例
  direct-server:
    type: direct
    ssh:
      host: "192.168.1.100"
      port: 22
      username: "user"
      key_file: "~/.ssh/id_rsa"
      timeout: 10
    session:
      name: "direct-session"
      working_directory: "/home/user"
      environment: {}
      shell: "/bin/bash"

# 安全配置
security:
  allowed_commands:
    - "ls"
    - "pwd"
    - "cd"
    - "cat"
    - "grep"
    - "find"
    - "git"
    - "python"
    - "node"
    - "npm"
    - "pip"
  
  blocked_commands:
    - "rm -rf /"
    - "sudo rm"
    - "mkfs"
  
  command_timeout: 300
  max_output_size: 10485760
  max_concurrent_commands: 10
"""
    
    output_path = Path(output) if output else Path("cursor_bridge_config.yaml")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    click.echo(f"✅ 配置文件已生成: {output_path}")


@cli.command()
@click.pass_context
def mcp(ctx):
    """启动MCP服务器（用于Cursor集成）"""
    async def _mcp():
        config_path = ctx.obj.get('config')
        
        # 导入MCP服务器
        from .mcp_server import run_stdio_server
        
        click.echo("🔗 启动MCP服务器...")
        click.echo("📝 日志文件: /tmp/cursor-bridge-mcp.log")
        
        try:
            await run_stdio_server(config_path)
        except KeyboardInterrupt:
            click.echo("\n⏹️  MCP服务器已关闭")
        except Exception as e:
            click.echo(f"❌ MCP服务器启动失败: {e}")
            raise
    
    asyncio.run(_mcp())


@cli.command()
def version():
    """显示版本信息"""
    click.echo("Cursor Bridge v0.1.0")
    click.echo("企业远程开发解决方案")


if __name__ == '__main__':
    cli()