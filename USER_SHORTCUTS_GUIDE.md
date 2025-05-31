# 🚀 常用命令和目录配置指南

## 📋 概述

cursor-bridge现在支持**智能常用命令系统**，你可以通过自然语言调用预配置的命令和目录，大大提高远程开发效率！

## 🎯 如何使用

### 1. 常用目录导航

你可以这样说：

```
请进入我的代码目录
请切换到工作空间目录
请查看日志目录的内容
请进入模型目录
```

**预配置的目录**：
- **home**: `/home` - 主目录
- **code**: `/home/Code` - 代码目录
- **projects**: `/home/Code` - 项目目录
- **workspace**: `/workspace` - 工作空间
- **models**: `/workspace/models` - 模型目录
- **data**: `/workspace/data` - 数据目录
- **logs**: `/var/log` - 日志目录
- **scripts**: `/home/scripts` - 脚本目录

### 2. 常用命令执行

你可以这样说：

```
请检查系统状态
请查看GPU状态
请检查内存使用情况
请查看磁盘使用情况
请检查Python环境
请查看Git状态
请检查Docker状态
```

## 📊 预配置的常用命令

### 系统监控类

#### `system_status` - 系统状态检查
```bash
df -h && free -h && ps aux | head -10
```
**用法**: "请检查系统状态" 或 "帮我看看系统状态"

#### `gpu_status` - GPU状态检查
```bash
nvidia-smi
```
**用法**: "请查看GPU状态" 或 "检查一下GPU"

#### `memory_usage` - 内存使用情况
```bash
free -h && ps aux --sort=-%mem | head -10
```
**用法**: "请查看内存使用情况" 或 "检查内存状态"

#### `disk_usage` - 磁盘使用情况
```bash
df -h && du -sh /home/* 2>/dev/null | sort -hr | head -10
```
**用法**: "请查看磁盘使用情况" 或 "检查磁盘空间"

### 开发相关类

#### `python_env` - Python环境检查
```bash
python --version && which python && pip list | head -10
```
**用法**: "请检查Python环境" 或 "查看Python版本"

#### `git_status` - Git状态检查
```bash
git status && git log --oneline -5
```
**用法**: "请查看Git状态" 或 "检查代码状态"

#### `docker_status` - Docker状态检查
```bash
docker ps && docker images | head -5
```
**用法**: "请检查Docker状态" 或 "查看容器状态"

### 日志查看类

#### `recent_logs` - 最近日志
```bash
tail -50 /var/log/syslog 2>/dev/null || journalctl -n 50
```
**用法**: "请查看最近的日志" 或 "看看系统日志"

#### `error_logs` - 错误日志
```bash
grep -i error /var/log/* 2>/dev/null | tail -10
```
**用法**: "请查找错误日志" 或 "有什么错误吗"

### 网络和进程类

#### `network_status` - 网络状态
```bash
ip addr show && netstat -tuln | head -10
```
**用法**: "请检查网络状态" 或 "查看网络连接"

#### `top_processes` - 占用资源最多的进程
```bash
ps aux --sort=-%cpu | head -10
```
**用法**: "请查看占用资源最多的进程" 或 "哪些进程在消耗CPU"

## 🔄 工作流组合

### `full_system_check` - 完整系统检查
执行：系统状态 + GPU状态 + 磁盘使用 + 进程监控

**用法**: "请做一个完整的系统检查" 或 "全面检查一下系统"

### `dev_environment_check` - 开发环境检查
执行：Python环境 + Git状态 + Docker状态

**用法**: "请检查开发环境" 或 "确认一下开发环境是否正常"

### `troubleshooting` - 故障排查
执行：最近日志 + 错误日志 + 内存使用 + 网络状态

**用法**: "请帮我排查问题" 或 "系统有什么异常吗"

## 🎨 自然语言示例

你可以用各种自然语言方式来调用这些命令：

### 直接调用
```
请检查GPU状态
帮我看看内存使用情况
查看一下磁盘空间
```

### 问题式
```
GPU现在怎么样？
内存够用吗？
磁盘空间还有多少？
```

### 任务式
```
我想了解系统当前状态
帮我确认开发环境是否正常
需要排查一下系统问题
```

## ⚙️ 自定义你的常用命令

### 添加新的常用目录

编辑 `cursor_bridge_config.yaml` 文件，在 `user_shortcuts.directories` 部分添加：

```yaml
user_shortcuts:
  directories:
    my_project: "/home/Code/my-important-project"
    backup: "/home/backup"
    temp: "/tmp"
```

### 添加新的常用命令

在 `user_shortcuts.commands` 部分添加：

```yaml
user_shortcuts:
  commands:
    my_custom_check:
      description: "我的自定义检查"
      command: "echo 'Hello' && date && whoami"
      
    project_status:
      description: "检查项目状态"
      command: "cd /home/Code/my-project && git status && npm test"
```

### 创建自定义工作流

在 `user_shortcuts.workflows` 部分添加：

```yaml
user_shortcuts:
  workflows:
    my_daily_check:
      description: "我的日常检查"
      commands:
        - "system_status"
        - "my_custom_check"
        - "project_status"
```

## 🔍 智能建议系统

系统会根据你的话语中的关键词自动建议合适的命令：

- 说到"**检查**" → 建议 system_status, gpu_status, python_env
- 说到"**GPU**" → 建议 gpu_status
- 说到"**内存**" → 建议 memory_usage
- 说到"**日志**" → 建议 recent_logs, error_logs
- 说到"**状态**" → 建议 system_status, git_status, docker_status

## 💡 使用技巧

### 1. 组合使用
```
请先检查系统状态，然后查看GPU状态，最后看看有没有错误日志
```

### 2. 条件执行
```
如果GPU使用率很高，请查看占用GPU的进程
```

### 3. 定期检查
```
请每天帮我做一次完整的系统检查
```

### 4. 问题导向
```
系统运行很慢，请帮我排查原因
```

## 🚀 开始使用

现在你可以在Cursor中尝试这些命令：

```
你好！请帮我检查一下系统状态，看看GPU和内存使用情况。
```

```
我想了解一下开发环境是否正常，请检查Python、Git和Docker的状态。
```

```
请进入我的代码目录，然后查看最近的Git提交记录。
```

---

**记住**：你可以用最自然的语言来描述你想做的事情，AI会智能地匹配到合适的预配置命令！🎉 