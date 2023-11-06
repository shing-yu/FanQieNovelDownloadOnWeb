# 使用官方的Python基础镜像
FROM python:3.9
LABEL authors="weiwei"

# 设置工作目录
WORKDIR /app

# 复制项目文件到工作目录
COPY . /app/

# 安装系统依赖 (如果需要)
# RUN apt-get update && apt-get install -y <system-packages>

# 安装 Python 依赖
RUN pip install -r requirements.txt

# 执行数据库迁移
RUN python manage.py migrate

# 暴露应用所使用的端口 (根据需要)
# EXPOSE 8000

# 启动 Django 应用
CMD ["python", "manage.py", "runserver", "[::]:8000"]
