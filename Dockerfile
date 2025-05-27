FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    openssh-client \
    tmux \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt pyproject.toml ./

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码
COPY src/ ./src/
COPY config/ ./config/

# 设置环境变量
ENV PYTHONPATH=/app/src
ENV CONFIG_PATH=/app/config/cursor_bridge_config.yaml

# 暴露端口
EXPOSE 8082 8083 9090

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8083/health || exit 1

# 启动命令
CMD ["python", "-m", "cursor_bridge.server"]