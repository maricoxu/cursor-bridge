.PHONY: help install dev test lint format clean build docker run stop logs

# 默认目标
help:
	@echo "Cursor Bridge - 开发工具命令"
	@echo ""
	@echo "可用命令:"
	@echo "  install     安装项目依赖"
	@echo "  dev         安装开发依赖"
	@echo "  test        运行测试"
	@echo "  lint        代码检查"
	@echo "  format      代码格式化"
	@echo "  clean       清理临时文件"
	@echo "  build       构建项目"
	@echo "  docker      构建Docker镜像"
	@echo "  run         启动服务"
	@echo "  stop        停止服务"
	@echo "  logs        查看日志"

# 安装依赖
install:
	pip install -r requirements.txt

# 安装开发依赖
dev:
	poetry install --with dev
	pre-commit install

# 运行测试
test:
	pytest tests/ -v --cov=src/cursor_bridge --cov-report=html

# 代码检查
lint:
	flake8 src/ tests/
	mypy src/
	bandit -r src/

# 代码格式化
format:
	black src/ tests/
	isort src/ tests/

# 清理临时文件
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/

# 构建项目
build:
	poetry build

# 构建Docker镜像
docker:
	docker build -t cursor-bridge:latest .

# 启动服务
run:
	python -m cursor_bridge.server --config config/cursor_bridge_config.yaml

# 使用Docker Compose启动
run-docker:
	docker-compose up -d

# 停止Docker服务
stop:
	docker-compose down

# 查看日志
logs:
	docker-compose logs -f cursor-bridge

# 开发模式启动（带调试）
dev-run:
	LOG_LEVEL=DEBUG python -m cursor_bridge.server --config config/cursor_bridge_config.yaml --verbose

# 运行集成测试
test-integration:
	pytest tests/ -v -m integration

# 生成文档
docs:
	mkdocs build

# 启动文档服务器
docs-serve:
	mkdocs serve

# 发布到PyPI
publish:
	poetry publish --build

# 检查项目状态
status:
	@echo "=== 项目状态 ==="
	@echo "Python版本: $(shell python --version)"
	@echo "Poetry版本: $(shell poetry --version)"
	@echo "Git分支: $(shell git branch --show-current)"
	@echo "Git状态: $(shell git status --porcelain | wc -l) 个未提交的更改"
	@echo ""
	@echo "=== 服务状态 ==="
	@curl -s http://localhost:8083/health || echo "服务未运行"