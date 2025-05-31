# 🎯 智能项目管理系统使用指南

## 📋 概述

cursor-bridge现在支持**智能项目管理系统**，能够自动识别你正在讨论的项目，并智能切换到对应的目录和环境。再也不用手动切换目录了！

## 🚀 核心功能

### 1. 智能项目识别

AI会根据你的对话内容自动识别项目：

```
你: "我们来编译XMLIR项目"
AI: 🎯 识别到项目: XMLIR
    📁 自动切换到: /home/Code/baidu/xpu/XMLIR
    🔧 执行编译命令...
```

### 2. 项目上下文记忆

系统会记住你最近讨论的项目：

```
你: "检查一下编译状态"
AI: 💭 当前项目: XMLIR
    🔍 在XMLIR项目中检查编译状态...
```

### 3. 项目特定命令

每个项目都有预配置的专用命令：

```
你: "编译一下项目"
AI: 🎯 当前项目: XMLIR
    ⚡ 执行: bash script/build/cmake_build.sh -p
```

## 📁 已配置的项目

### 🔧 XMLIR (当前活跃项目)
- **路径**: `/home/Code/baidu/xpu/XMLIR`
- **描述**: 百度XPU XMLIR编译器项目
- **关键词**: xmlir, XMLIR, 编译器, compiler, xpu

**专用命令**:
- **编译**: `bash script/build/cmake_build.sh -p`
- **清理重编**: `rm -rf build && bash script/build/cmake_build.sh -p`
- **运行测试**: `bash script/test/run_tests.sh`
- **检查状态**: `git status && ls -la`
- **环境设置**: `source setup_env.sh`

### 🌊 Hydra
- **路径**: `/home/Code/baidu/xpu/Hydra`
- **描述**: 百度XPU Hydra项目
- **关键词**: hydra, Hydra, xpu

### 🧮 xBLAS
- **路径**: `/home/Code/baidu/xpu/xBLAS`
- **描述**: 百度XPU xBLAS项目
- **关键词**: xblas, xBLAS, BLAS, 线性代数

### 🔥 PyTorch
- **路径**: `/home/Code/pytorch`
- **描述**: PyTorch深度学习框架
- **关键词**: pytorch, PyTorch, 深度学习, 机器学习, AI

### 🚀 Megatron-LM
- **路径**: `/home/Code/Megatron-LM`
- **描述**: 大规模语言模型训练框架
- **关键词**: megatron, Megatron, LLM, 大模型, 训练

### ⚡ Flux
- **路径**: `/home/Code/flux`
- **描述**: Flux项目
- **关键词**: flux, Flux

## 💬 自然语言使用示例

### 项目切换
```
"我们切换到PyTorch项目"
"现在开发Hydra项目"
"我想看看Megatron的代码"
```

### 项目编译
```
"编译XMLIR项目"
"重新编译一下"
"清理并重新编译"
"编译PyTorch"
```

### 项目状态检查
```
"检查项目状态"
"看看编译进度"
"项目有什么变化吗"
"Git状态怎么样"
```

### 项目测试
```
"运行测试"
"测试一下项目"
"执行单元测试"
```

### 项目环境
```
"设置开发环境"
"配置项目环境"
"初始化环境"
```

## 🎨 智能识别机制

### 1. 关键词匹配
系统会根据对话中的关键词自动识别项目：

- 提到"XMLIR"、"编译器" → 识别为XMLIR项目
- 提到"PyTorch"、"深度学习" → 识别为PyTorch项目
- 提到"Megatron"、"大模型" → 识别为Megatron项目

### 2. 上下文记忆
系统会记住最近5个讨论的项目，优先匹配当前上下文。

### 3. 路径匹配
如果你提到具体路径，系统会自动匹配对应项目。

## 🔧 项目切换行为

当识别到新项目时，系统会自动：

1. **切换目录**: `cd /path/to/project`
2. **设置环境变量**: 加载项目特定的环境变量
3. **显示确认**: 告诉你已切换到哪个项目
4. **执行初始命令**: `pwd` 和 `ls -la` 显示当前状态

## ⚙️ 自定义项目

你可以在 `cursor_bridge_config.yaml` 中添加新项目：

```yaml
project_management:
  projects:
    my_project:
      name: "我的项目"
      description: "项目描述"
      path: "/path/to/my/project"
      keywords: ["关键词1", "关键词2"]
      
      commands:
        build:
          description: "编译项目"
          command: "make build"
          
        test:
          description: "运行测试"
          command: "make test"
      
      environment:
        PROJECT_ROOT: "/path/to/my/project"
        BUILD_TYPE: "Debug"
```

## 📊 项目状态管理

### 当前项目状态
系统会跟踪：
- 当前活跃项目
- 最近访问的项目
- 项目工作状态

### 状态持久化
项目状态会自动保存到 `/tmp/cursor_bridge_project_state.json`，重启后恢复。

## 💡 使用技巧

### 1. 明确项目名称
```
✅ "编译XMLIR项目"
✅ "切换到PyTorch"
❌ "编译一下"（不明确是哪个项目）
```

### 2. 利用关键词
```
✅ "检查编译器项目状态"（会识别为XMLIR）
✅ "深度学习框架有更新吗"（会识别为PyTorch）
```

### 3. 组合操作
```
"切换到XMLIR项目，然后编译，最后运行测试"
```

### 4. 上下文延续
```
你: "切换到XMLIR项目"
AI: 已切换到XMLIR项目
你: "编译一下"（AI知道是编译XMLIR）
你: "运行测试"（AI知道是测试XMLIR）
```

## 🚀 实际使用示例

### 场景1：开始开发XMLIR
```
你: "我们来开发XMLIR编译器项目"
AI: 🎯 切换到XMLIR项目
    📁 当前目录: /home/Code/baidu/xpu/XMLIR
    🔧 项目环境已设置
    
你: "先编译一下看看"
AI: ⚡ 执行XMLIR编译命令
    🔄 bash script/build/cmake_build.sh -p
    ✅ 编译开始...
```

### 场景2：检查项目状态
```
你: "PyTorch项目最近有什么变化"
AI: 🎯 切换到PyTorch项目
    📁 当前目录: /home/Code/pytorch
    🔍 检查Git状态...
    📊 显示最近提交和文件变化
```

### 场景3：多项目开发
```
你: "先检查XMLIR的编译状态，然后切换到PyTorch运行测试"
AI: 🎯 在XMLIR项目中检查编译状态
    ✅ 编译状态正常
    🔄 切换到PyTorch项目
    🧪 运行PyTorch测试...
```

## 🎉 开始使用

现在你可以直接说：

```
"我们来编译XMLIR项目"
"检查一下PyTorch的状态"
"切换到Megatron项目运行训练"
"Hydra项目有什么更新吗"
```

AI会自动理解你的意图，切换到对应项目，并执行相应操作！

---

**记住**: 只需要自然地描述你想做什么，AI会智能地处理项目切换和命令执行！🎯 