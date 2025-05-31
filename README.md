# Cursor Bridge

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![GitHub repo](https://img.shields.io/badge/GitHub-cursor--bridge-blue.svg)](https://github.com/maricoxu/cursor-bridge)

🚀 **让Cursor AI在你的远程服务器上执行命令** - 基于tmux会话的简单远程开发解决方案

## 🎯 核心思路

你已经在tmux中手动建立了到远程服务器的连接，cursor-bridge让Cursor的AI能够在这些会话中执行命令：

```
Cursor AI → cursor-bridge → 你的tmux会话 → 远程服务器
                              ↑
                        你手动建立的连接
```

## ✨ 核心特性

- 🔄 **复用现有连接**: 基于你已手动建立的tmux会话
- 🎯 **零网络配置**: 不处理SSH/VPN，专注于命令执行
- ⚡ **即时响应**: 通过tmux实现毫秒级命令执行
- 🔧 **简单配置**: 只需配置tmux会话名称
- 🛡️ **安全可靠**: 基于你现有的安全架构

## 🚀 快速开始

### 前提条件

1. **Python 3.9+** 和 **tmux** 已安装
2. **已建立的远程连接**: 你需要在tmux会话中已经连接到远程服务器

### 安装步骤

#### 1. 克隆项目并安装

```bash
git clone https://github.com/maricoxu/cursor-bridge.git
cd cursor-bridge
./install.sh
```

#### 2. 建立远程连接

```bash
# 创建tmux会话并连接到远程服务器
tmux new-session -d -s baidu-server
tmux send-keys -t baidu-server "ssh user@your-server" Enter

# 验证连接（可选）
tmux attach -t baidu-server
# 确认已连接到远程服务器，然后按 Ctrl+B, D 分离会话
```

#### 3. 配置cursor-bridge

编辑 `cursor_bridge_config.local.yaml`：

```yaml
servers:
  baidu-server:
    type: local_tmux
    tmux:
      session_name: "baidu-server"  # 你的tmux会话名
      window_name: "main"
    session:
      name: "baidu-dev-session"
      working_directory: "/home/your-username"  # 远程服务器工作目录
      environment:
        TERM: "xterm-256color"
      shell: "/bin/bash"

# 其他配置...
```

#### 4. 配置Cursor IDE

将 `cursor_mcp_config.json` 的内容添加到Cursor的MCP设置中：

1. 打开Cursor IDE
2. 按 `Cmd+,` 打开设置
3. 搜索 "MCP" 
4. 添加配置内容
5. 重启Cursor

### 🧪 测试

```bash
# 测试配置
export PYTHONPATH=$PWD/src:$PYTHONPATH
python3 -m cursor_bridge.cli --config cursor_bridge_config.local.yaml config

# 测试MCP服务器
./start_cursor_bridge.sh
```

## 🎯 使用示例

在Cursor中，你可以直接与AI对话：

```
你: "请在远程服务器上检查GPU状态"
AI: 我来帮你检查GPU状态
    [执行] nvidia-smi
    [输出] GPU状态信息...

你: "请切换到我的项目目录并查看文件"
AI: [执行] cd /home/Code/my-project && ls -la
    [输出] 项目文件列表...

你: "请运行我的训练脚本"
AI: [执行] python train.py --config config.yaml
    [输出] 训练开始...
```

## 🏗️ 架构说明

### 工作流程

当Cursor AI执行 `nvidia-smi` 时：

1. **cursor-bridge**: `tmux send-keys -t baidu-server "nvidia-smi" Enter`
2. **等待执行**: 等待1秒让命令完成
3. **捕获输出**: `tmux capture-pane -t baidu-server -p`
4. **返回结果**: 将输出返回给Cursor AI

### 架构图

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Cursor IDE    │    │  cursor-bridge   │    │   Local tmux    │
│                 │    │                  │    │    Session      │
│  ┌───────────┐  │    │  ┌─────────────┐ │    │  ┌───────────┐  │
│  │    AI     │◄─┼────┼─►│ MCP Server  │ │    │  │ baidu-    │  │
│  │  Agent    │  │    │  └─────────────┘ │    │  │ server    │  │
│  └───────────┘  │    │  ┌─────────────┐ │    │  └───────────┘  │
└─────────────────┘    │  │ Tmux        │◄┼────┼─►┌───────────┐  │
                       │  │ Controller  │ │    │  │    SSH    │  │
                       │  └─────────────┘ │    │  │connection │  │
                       └──────────────────┘    │  └───────────┘  │
                                               └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │  Remote Server  │
                                               └─────────────────┘
```

## 📁 项目结构

```
cursor-bridge/
├── src/cursor_bridge/           # 核心代码
│   ├── cli.py                   # 命令行接口
│   ├── mcp_server.py           # MCP服务器
│   ├── config/                 # 配置管理
│   └── utils/                  # 工具函数
├── cursor_bridge_config.local.yaml  # 本地配置
├── cursor_mcp_config.json      # Cursor MCP配置
├── install.sh                  # 安装脚本
├── start_cursor_bridge.sh      # 启动脚本
├── requirements.txt            # Python依赖
└── README.md                   # 项目说明
```

## ⚙️ 配置参考

### 基本配置

```yaml
# cursor_bridge_config.local.yaml
servers:
  # 主要开发服务器
  main-server:
    type: local_tmux
    tmux:
      session_name: "dev"
      window_name: "main"
    session:
      name: "main-dev-session"
      working_directory: "/home/Code"
      environment:
        TERM: "xterm-256color"
      shell: "/bin/bash"

  # 百度服务器
  baidu-server:
    type: local_tmux
    tmux:
      session_name: "baidu"
      window_name: "server"
    session:
      name: "baidu-dev-session"
      working_directory: "/workspace"
      environment:
        TERM: "xterm-256color"
      shell: "/bin/bash"

# 默认服务器
default_server: "baidu-server"

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
    - "python3"
    - "nvidia-smi"
    - "htop"
    - "ps"
  
  command_timeout: 300
  max_output_size: 10485760
```

### 多服务器配置

你可以配置多个tmux会话对应不同的服务器：

```bash
# 创建多个会话
tmux new-session -d -s dev-server
tmux new-session -d -s test-server
tmux new-session -d -s prod-server

# 在不同会话中连接不同服务器
tmux send-keys -t dev-server "ssh dev@dev-server.com" Enter
tmux send-keys -t test-server "ssh test@test-server.com" Enter
tmux send-keys -t prod-server "ssh prod@prod-server.com" Enter
```

## 🔧 故障排除

### 常见问题

#### 1. tmux会话不存在
```bash
# 检查tmux会话
tmux list-sessions

# 重新创建会话
tmux new-session -d -s your-session-name
```

#### 2. 命令执行失败
```bash
# 检查tmux会话状态
tmux capture-pane -t your-session-name -p

# 手动测试命令
tmux send-keys -t your-session-name "pwd" Enter
```

#### 3. Cursor连接失败
```bash
# 测试MCP服务器
export PYTHONPATH=$PWD/src:$PYTHONPATH
python3 -m cursor_bridge.cli --config cursor_bridge_config.local.yaml mcp
```

### 调试模式

```bash
# 启用详细日志
export LOG_LEVEL=DEBUG
./start_cursor_bridge.sh
```

## 🛠️ 开发

### 本地开发

```bash
# 安装开发依赖
pip3 install -r requirements.txt

# 运行测试
python3 -m pytest tests/

# 代码格式化
black src/ tests/
```

### 添加新功能

1. 编辑 `src/cursor_bridge/` 下的相关文件
2. 更新配置模型（如需要）
3. 添加测试
4. 更新文档

## 📝 更新日志

### v0.1.0 (当前版本)
- ✅ 基于tmux的命令执行
- ✅ 简化的配置管理
- ✅ Cursor MCP集成
- ✅ 自动安装脚本

### 计划功能
- 🔄 多窗口支持
- 🔄 命令历史记录
- 🔄 交互式命令支持
- 🔄 会话状态监控

## 🤝 贡献

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 创建Pull Request

## 📄 许可证

MIT License - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Cursor IDE](https://cursor.sh/) - 优秀的AI代码编辑器
- [tmux](https://github.com/tmux/tmux) - 强大的终端复用器
- [Model Context Protocol](https://github.com/modelcontextprotocol) - MCP协议

---

**让远程开发像本地一样自然** 🚀

有问题？查看 [Issues](https://github.com/maricoxu/cursor-bridge/issues) 或创建新的Issue。