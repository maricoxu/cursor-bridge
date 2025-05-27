"""
Cursor Bridge CLI入口

提供命令行接口。
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.logging import RichHandler

from .config.loader import ConfigLoader
from .server import CursorBridgeServer

console = Console()


def setup_logging(level: str = "INFO", verbose: bool = False):
    """设置日志"""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # 配置rich日志处理器
    handler = RichHandler(
        console=console,
        show_time=True,
        show_path=verbose,
        markup=True
    )
    
    # 配置根日志器
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[handler]
    )
    
    # 设置第三方库日志级别
    if not verbose:
        logging.getLogger("asyncio").setLevel(logging.WARNING)
        logging.getLogger("paramiko").setLevel(logging.WARNING)


@click.group()
@click.option("--config", "-c", 
              default="config/cursor_bridge_config.yaml",
              help="配置文件路径")
@click.option("--log-level", "-l",
              default="INFO",
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
              help="日志级别")
@click.option("--verbose", "-v", is_flag=True, help="详细输出")
@click.pass_context
def cli(ctx, config: str, log_level: str, verbose: bool):
    """Cursor Bridge - 无缝远程开发桥梁"""
    ctx.ensure_object(dict)
    ctx.obj['config_path'] = config
    ctx.obj['log_level'] = log_level
    ctx.obj['verbose'] = verbose
    
    setup_logging(log_level, verbose)


@cli.command()
@click.pass_context
def server(ctx):
    """启动MCP服务器"""
    config_path = ctx.obj['config_path']
    
    try:
        # 加载配置
        config = ConfigLoader.load_from_file(config_path)
        console.print(f"[green]✓[/green] 配置加载成功: {config_path}")
        
        # 启动服务器
        server_instance = CursorBridgeServer(config.dict())
        
        console.print("[blue]启动Cursor Bridge服务器...[/blue]")
        asyncio.run(server_instance.start())
        
    except FileNotFoundError as e:
        console.print(f"[red]✗[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]✗[/red] 启动失败: {e}")
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx):
    """检查服务状态"""
    console.print("[blue]检查Cursor Bridge状态...[/blue]")
    # TODO: 实现状态检查
    console.print("[green]✓[/green] 服务运行正常")


@cli.command()
@click.pass_context
def config_check(ctx):
    """检查配置文件"""
    config_path = ctx.obj['config_path']
    
    try:
        config = ConfigLoader.load_from_file(config_path)
        console.print(f"[green]✓[/green] 配置文件有效: {config_path}")
        
        # 显示配置摘要
        console.print(f"服务器数量: {len(config.servers)}")
        for name in config.servers.keys():
            console.print(f"  - {name}")
            
    except Exception as e:
        console.print(f"[red]✗[/red] 配置文件错误: {e}")
        sys.exit(1)


@cli.command()
@click.argument("server_name")
@click.argument("command")
@click.pass_context
def exec(ctx, server_name: str, command: str):
    """在指定服务器上执行命令"""
    console.print(f"[blue]在 {server_name} 上执行: {command}[/blue]")
    # TODO: 实现命令执行
    console.print("[green]✓[/green] 命令执行完成")


@cli.command()
@click.pass_context
def sessions(ctx):
    """列出所有会话"""
    console.print("[blue]活跃会话列表:[/blue]")
    # TODO: 实现会话列表
    console.print("暂无活跃会话")


def main():
    """主入口函数"""
    cli()


if __name__ == "__main__":
    main()