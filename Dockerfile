# 使用 Python Alpine 基础镜像
FROM python:3.9-alpine

# 更改 Alpine Linux 软件源
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories && apk update

# 设置时区为上海
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo "Asia/Shanghai" > /etc/timezone

# 设置工作目录
WORKDIR /app

# 安装依赖，使用清华源
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用代码
COPY . .

# 创建数据库目录
RUN mkdir -p /app/data

# 设置服务器地址环境变量，可在运行时覆盖
ENV SERVER_URL=http://127.0.0.1:5000
#是否使用零宽字符模式
ENV USE_ZWS=false

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
