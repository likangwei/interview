# 使用官方 Python 3.10 slim 版
FROM python:3.10-slim

# 设置环境变量，减少输出缓存，避免时区交互
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=Asia/Shanghai

# 设置工作目录
WORKDIR /app

# 安装 ffmpeg 和依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装（先复制 requirements，避免每次改代码都重新装库）
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 复制项目代码
COPY . .

# 创建视频目录（如果你有挂载卷，可以省略）
RUN mkdir -p /app/videos

# 暴露端口
EXPOSE 8000

# 启动 FastAPI 服务
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
