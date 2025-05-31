# Cursor IDE 使用指南

## 🎯 现在就开始使用！

你已经完成了cursor-bridge的安装，现在让我们一步步配置Cursor IDE并开始试用。

## 📋 第一步：配置Cursor IDE

### 1. 打开Cursor IDE设置

- **macOS**: 按 `Cmd + ,`
- **Windows/Linux**: 按 `Ctrl + ,`

### 2. 找到MCP设置

在设置搜索框中输入 "MCP" 或 "Model Context Protocol"

### 3. 添加MCP服务器配置

将以下配置添加到MCP服务器设置中：

```json
{
  "mcpServers": {
    "cursor-bridge": {
      "command": "python3",
      "args": [
        "-m", 
        "cursor_bridge.cli", 
        "--config", 
        "/Users/xuyehua/Code/cursor-bridge/cursor_bridge_config.yaml",
        "mcp"
      ],
      "env": {
        "PYTHONPATH": "/Users/xuyehua/Code/cursor-bridge/src"
      }
    }
  }
}
```

### 4. 保存并重启Cursor

- 保存设置
- 完全关闭Cursor IDE
- 重新启动Cursor IDE

## 🔍 第二步：验证连接

### 检查MCP连接状态

重启后，你应该能看到：
- 状态栏显示MCP服务器已连接
- 或者在设置中看到cursor-bridge服务器状态为"已连接"

### 如果连接失败

1. **检查tmux会话**：
   ```bash
   tmux list-sessions
   # 应该看到 baidu-session
   ```

2. **手动测试MCP服务器**：
   ```bash
   cd /Users/xuyehua/Code/cursor-bridge
   ./verify_setup.sh
   ```

## 🧪 第三步：开始试用

### 基础测试命令

在Cursor中，打开一个新的聊天窗口，尝试以下对话：

#### 测试1：检查当前目录
```
请在远程服务器上执行 pwd 命令，告诉我当前在哪个目录
```

#### 测试2：查看目录内容
```
请在远程服务器上运行 ls -la 命令，显示当前目录的详细内容
```

#### 测试3：检查系统信息
```
请在远程服务器上运行以下命令：
1. whoami - 查看当前用户
2. uname -a - 查看系统信息
3. date - 查看当前时间
```

### 进阶测试命令

#### 测试4：开发环境检查
```
请帮我检查远程服务器的开发环境：
1. python --version
2. git --version
3. which python3
4. echo $PATH
```

#### 测试5：系统监控
```
请帮我监控远程服务器的状态：
1. df -h - 查看磁盘使用情况
2. free -h - 查看内存使用情况
3. ps aux | head -10 - 查看运行进程
```

#### 测试6：如果有GPU
```
请检查远程服务器的GPU状态：
1. nvidia-smi
2. echo $CUDA_VISIBLE_DEVICES
```

## 💡 使用技巧

### 1. 自然语言交互

你可以用自然语言描述你想做的事情：

```
我想在远程服务器上创建一个新的Python项目目录，然后初始化git仓库
```

```
帮我检查远程服务器上是否有某个特定的文件，如果没有就创建它
```

```
我需要在远程服务器上安装一些Python包，请帮我检查pip是否可用
```

### 2. 复杂任务分解

AI会自动将复杂任务分解为多个步骤：

```
请帮我在远程服务器上设置一个新的Python虚拟环境，并安装numpy和pandas
```

### 3. 错误处理

如果命令执行失败，AI会帮你分析错误并提供解决方案：

```
我刚才的命令执行失败了，请帮我分析错误原因并提供解决方案
```

## 🔧 常见使用场景

### 场景1：代码开发
```
请在远程服务器上：
1. 进入我的项目目录 /workspace/my-project
2. 查看git状态
3. 如果有未提交的更改，显示给我看
```

### 场景2：环境配置
```
请帮我在远程服务器上：
1. 检查Python环境
2. 创建一个新的虚拟环境
3. 激活虚拟环境并安装requirements.txt中的依赖
```

### 场景3：日志分析
```
请帮我查看远程服务器上的应用日志：
1. 查看最新的100行日志
2. 搜索包含"ERROR"的日志条目
3. 统计错误数量
```

### 场景4：性能监控
```
请帮我监控远程服务器的性能：
1. 查看CPU使用率
2. 查看内存使用情况
3. 查看磁盘I/O状态
4. 如果发现异常，请告诉我
```

## ⚠️ 注意事项

### 1. 安全考虑
- 只在你信任的服务器上使用
- 避免执行可能损坏系统的命令
- 定期检查命令执行日志

### 2. 网络连接
- 确保tmux会话保持活跃
- 如果连接断开，重新建立tmux会话

### 3. 权限管理
- 确保你有执行相关命令的权限
- 某些系统命令可能需要sudo权限

## 🆘 故障排除

### 问题1：AI说找不到远程服务器
**解决方案**：
```bash
# 检查tmux会话
tmux list-sessions
# 如果没有baidu-session，创建一个
tmux new-session -d -s baidu-session
```

### 问题2：命令执行超时
**解决方案**：
- 检查网络连接
- 尝试执行简单命令如 `echo hello`
- 重启tmux会话

### 问题3：MCP服务器连接失败
**解决方案**：
```bash
# 运行验证脚本
cd /Users/xuyehua/Code/cursor-bridge
./verify_setup.sh

# 手动测试MCP服务器
export PYTHONPATH=/Users/xuyehua/Code/cursor-bridge/src:$PYTHONPATH
python3 -m cursor_bridge.cli --config cursor_bridge_config.yaml mcp
```

## 🎉 开始享受远程开发！

现在你已经准备好了！在Cursor中开始与AI对话，让它帮你在远程服务器上执行各种任务。记住，你可以用自然语言描述你想做的事情，AI会帮你转换为具体的命令并执行。

**试试这个简单的开始**：
```
你好！请帮我在远程服务器上执行 pwd 命令，然后告诉我当前在哪个目录。
``` 