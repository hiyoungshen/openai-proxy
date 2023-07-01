# 基础镜像
FROM python:3.10

# 设置工作目录
WORKDIR /app

# 将项目文件复制到镜像中
COPY . /app

# 安装项目依赖项
RUN pip install -r requirements.txt

# 暴露端口（如果需要）
EXPOSE 5000

# 定义容器启动时的命令
CMD ["python", "main.py"]