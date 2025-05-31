# Cursor IDE MCP 设置指南

## 🎯 快速设置

### 1. 确保安装完成
确保你已经运行了 `./install.sh` 并且所有依赖都已安装。

### 2. 创建tmux会话（如果还没有）
```bash
# 创建测试会话
tmux new-session -d -s baidu-session

# 如果你要连接到远程服务器，在会话中运行连接命令
# tmux send-keys -t baidu-session "relay-cli connect your-server" Enter
# 或者
# tmux send-keys -t baidu-session "ssh user@remote-server" Enter
```

### 3. 配置Cursor IDE

#### 方法1：通过Cursor设置界面
1. 打开Cursor IDE
2. 按 `Cmd+,` (macOS) 或 `Ctrl+,` (Windows/Linux) 打开设置
3. 搜索 "MCP" 或找到 "Model Context Protocol" 设置
4. 添加新的MCP服务器配置：
   ```json
   {
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
   ```

#### 方法2：直接编辑配置文件
1. 找到Cursor的配置文件：
   - macOS: `~/Library/Application Support/Cursor/User/settings.json`
   - Windows: `%APPDATA%\Cursor\User\settings.json`
   - Linux: `~/.config/Cursor/User/settings.json`

2. 在配置文件中添加或修改 `mcpServers` 部分：
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

### 4. 重启Cursor IDE
保存配置后，完全关闭并重新启动Cursor IDE。

### 5. 验证设置
在Cursor中，你应该能够：
1. 看到MCP服务器已连接（通常在状态栏或设置中显示）
2. 使用AI助手执行远程命令

## 🧪 测试命令

在Cursor中，你可以对AI说：

```
请在远程服务器上执行 pwd 命令
请检查远程服务器的当前目录内容
请在远程服务器上运行 ls -la
```

## 🔧 故障排除

### 问题1：MCP服务器无法启动
```bash
# 手动测试MCP服务器
export PYTHONPATH=/Users/xuyehua/Code/cursor-bridge/src:$PYTHONPATH
python3 -m cursor_bridge.cli --config cursor_bridge_config.yaml mcp
```

### 问题2：找不到tmux会话
```bash
# 检查tmux会话
tmux list-sessions

# 如果没有会话，创建一个
tmux new-session -d -s baidu-session
```

### 问题3：命令执行失败
检查配置文件中的tmux会话名称和窗口名称是否正确：
```bash
# 查看会话的窗口
tmux list-windows -t baidu-session
```

### 问题4：权限问题
确保Python脚本有执行权限：
```bash
chmod +x start_cursor_bridge.sh
```

## 📝 配置说明

### 主要配置文件
- `cursor_bridge_config.yaml`: 主配置文件，定义服务器和tmux会话
- `cursor_mcp_config.json`: Cursor IDE的MCP配置

### 重要路径
- 确保 `PYTHONPATH` 指向正确的src目录
- 确保配置文件路径是绝对路径
- 确保tmux会话名称与配置文件中的一致

## 🚀 高级用法

### 多服务器配置
你可以在 `cursor_bridge_config.yaml` 中配置多个服务器：
```yaml
servers:
  dev-server:
    type: local_tmux
    tmux:
      session_name: "dev-session"
      window_name: "zsh"
  
  prod-server:
    type: local_tmux
    tmux:
      session_name: "prod-session"
      window_name: "zsh"
```

### 环境变量配置
为不同的服务器设置不同的环境变量：
```yaml
servers:
  gpu-server:
    session:
      environment:
        CUDA_VISIBLE_DEVICES: "0,1,2,3"
        PYTHONPATH: "/workspace"
```

## 📞 获取帮助

如果遇到问题：
1. 查看 `README.md` 获取详细文档
2. 检查日志输出
3. 在GitHub上提交issue

---

**享受远程开发的便利！** 🎉 