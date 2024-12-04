# python环境
FROM python:3.10.15-slim

# 工作目录
WORKDIR /dg_spider
COPY . .

# 环境变量（删掉CFLAGS后安装cld会报错）
ENV CFLAGS="-Wno-narrowing"
ENV MY_ENV=prod

# 安装依赖
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    musl-dev \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt-dev \
 && pip install -r requirements.txt --no-cache-dir \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# 安装运行时依赖
RUN apt-get install -y \
    libssl3 \
    libxml2 \
    libxslt1.1

# 6801 flask
EXPOSE 6801

# 启动项目
CMD ["./start.sh"]
