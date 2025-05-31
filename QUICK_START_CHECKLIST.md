# 🚀 Cursor Bridge 快速开始检查清单

## ✅ 安装检查清单

### 第一步：环境准备
- [ ] Python 3.9+ 已安装
- [ ] tmux 已安装 (macOS: `brew install tmux`)
- [ ] 项目已克隆到本地

### 第二步：自动化安装
```bash
cd cursor-bridge
./install.sh
```
- [ ] 安装脚本运行成功
- [ ] 看到 "🎉 安装完成！" 消息

### 第三步：验证安装
```bash
./verify_setup.sh
```
- [ ] 所有测试通过
- [ ] 看到 "🎉 所有测试通过！" 消息

## 🔧 Cursor IDE 配置检查清单

### 第四步：获取配置
- [ ] 找到项目目录中的 `cursor_mcp_config.json` 文件
- [ ] 复制其中的JSON配置内容

### 第五步：配置Cursor IDE
- [ ] 打开Cursor IDE
- [ ] 按 `Cmd+,` (macOS) 或 `Ctrl+,` (Windows/Linux) 打开设置
- [ ] 搜索 "MCP" 找到Model Context Protocol设置
- [ ] 将JSON配置添加到MCP服务器设置中
- [ ] 保存设置

### 第六步：重启验证
- [ ] 完全关闭Cursor IDE
- [ ] 重新启动Cursor IDE
- [ ] 检查MCP服务器连接状态（应显示已连接）

## 🧪 功能测试检查清单

### 第七步：基础测试
在Cursor中尝试以下对话：

- [ ] **测试1**: "请在远程服务器上执行 pwd 命令"
  - 应该返回当前目录路径

- [ ] **测试2**: "请在远程服务器上运行 ls -la"
  - 应该显示目录内容列表

- [ ] **测试3**: "请在远程服务器上运行 echo hello"
  - 应该返回 "hello"

### 第八步：进阶测试
- [ ] **系统信息**: "请检查远程服务器的系统信息：whoami, uname -a, date"
- [ ] **环境检查**: "请检查Python版本：python --version"
- [ ] **自然语言**: "我想知道远程服务器的磁盘使用情况"

## 🔍 故障排除检查清单

### 如果MCP连接失败：
- [ ] 检查tmux会话：`tmux list-sessions`
- [ ] 重新运行验证：`./verify_setup.sh`
- [ ] 检查配置文件路径是否正确
- [ ] 重启Cursor IDE

### 如果命令执行失败：
- [ ] 确认tmux会话存在：`tmux list-sessions`
- [ ] 检查会话窗口：`tmux list-windows -t baidu-session`
- [ ] 手动测试MCP：
  ```bash
  export PYTHONPATH=/Users/xuyehua/Code/cursor-bridge/src:$PYTHONPATH
  python3 -m cursor_bridge.cli --config cursor_bridge_config.yaml mcp
  ```

## 📚 参考文档

- [ ] `README.md` - 完整项目文档
- [ ] `CURSOR_USAGE_GUIDE.md` - 详细使用指南
- [ ] `CURSOR_SETUP.md` - 配置说明
- [ ] `MCP_SETUP_SUMMARY.md` - 快速参考

## 🎉 成功标志

当你看到以下情况时，说明配置成功：

✅ **Cursor IDE中**：
- MCP服务器显示"已连接"状态
- AI能够响应远程命令请求
- 命令执行返回正确结果

✅ **命令行中**：
- `./verify_setup.sh` 全部通过
- `tmux list-sessions` 显示 baidu-session
- 手动MCP测试正常响应

## 🚀 开始使用

配置完成后，在Cursor中试试这个：

```
你好！请帮我在远程服务器上执行 pwd 命令，然后告诉我当前在哪个目录。接下来请运行 ls -la 显示目录内容。
```

如果AI能够成功执行这些命令并返回结果，恭喜你！🎉 你已经成功配置了cursor-bridge，可以开始享受远程开发的便利了！

---

**需要帮助？** 查看 `CURSOR_USAGE_GUIDE.md` 获取更多使用技巧和示例。 