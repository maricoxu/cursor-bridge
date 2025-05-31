# 🚀 常用命令快速参考

## 📁 常用目录

| 说法 | 目录路径 |
|------|----------|
| "进入代码目录" | `/home/Code` |
| "切换到工作空间" | `/workspace` |
| "查看日志目录" | `/var/log` |
| "进入模型目录" | `/workspace/models` |
| "查看数据目录" | `/workspace/data` |

## 🔧 系统监控命令

| 说法 | 执行的命令 |
|------|------------|
| "检查系统状态" | `df -h && free -h && ps aux \| head -10` |
| "查看GPU状态" | `nvidia-smi` |
| "检查内存使用" | `free -h && ps aux --sort=-%mem \| head -10` |
| "查看磁盘使用" | `df -h && du -sh /home/* \| sort -hr \| head -10` |
| "查看占用资源最多的进程" | `ps aux --sort=-%cpu \| head -10` |

## 💻 开发环境命令

| 说法 | 执行的命令 |
|------|------------|
| "检查Python环境" | `python --version && which python && pip list \| head -10` |
| "查看Git状态" | `git status && git log --oneline -5` |
| "检查Docker状态" | `docker ps && docker images \| head -5` |

## 📋 日志和网络命令

| 说法 | 执行的命令 |
|------|------------|
| "查看最近日志" | `tail -50 /var/log/syslog \|\| journalctl -n 50` |
| "查找错误日志" | `grep -i error /var/log/* \| tail -10` |
| "检查网络状态" | `ip addr show && netstat -tuln \| head -10` |

## 🔄 组合工作流

| 说法 | 执行内容 |
|------|----------|
| "完整系统检查" | 系统状态 + GPU状态 + 磁盘使用 + 进程监控 |
| "检查开发环境" | Python环境 + Git状态 + Docker状态 |
| "排查系统问题" | 最近日志 + 错误日志 + 内存使用 + 网络状态 |

## 💬 自然语言示例

### 直接命令
```
请检查GPU状态
帮我看看内存使用情况
查看一下磁盘空间
```

### 问题式
```
GPU现在怎么样？
内存够用吗？
有什么错误日志吗？
```

### 组合式
```
请先检查系统状态，然后看看GPU使用情况
我想了解开发环境是否正常
系统运行慢，帮我排查一下
```

## ⚙️ 自定义添加

在 `cursor_bridge_config.yaml` 中添加你的常用命令：

```yaml
user_shortcuts:
  directories:
    my_project: "/path/to/my/project"
    
  commands:
    my_check:
      description: "我的检查命令"
      command: "your command here"
```

---

**记住**: 用最自然的语言描述你想做的事情，AI会智能匹配！🎉 