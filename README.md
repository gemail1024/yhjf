# 阅后即焚消息系统

一个简单的阅后即焚消息系统，支持定时销毁和阅后即焚两种模式。

## 功能特点

- 🔥 阅后即焚：查看一次后消息自动销毁
- ⏰ 定时销毁：设定时间后消息自动销毁
- 🔒 密码保护：可选择为消息添加密码保护
- 🌓 暗色模式：支持浅色/深色主题切换
- 📱 移动适配：完美支持移动端浏览器
- 🔄 定时清理：自动清理过期消息

## 技术栈

- 后端：Python + Flask
- 数据库：SQLite
- 前端：HTML + CSS + JavaScript

## 快速开始

### Docker 部署（推荐）

1. 拉取镜像
```bash
docker pull scp96/yhjf:latest
```

2. 运行容器
```bash
docker run -d \
  -p 5000:5000 \
  -e SERVER_URL=http://your-domain.com \
  --name yhjf \
  scp96/yhjf:latest
```

### 手动部署

1. 克隆项目
```bash
git clone https://github.com/gemail1024/yhjf.git
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行项目
```bash
python app.py
```

4. 访问网站
```
http://127.0.0.1:5000
```

## 环境变量

可以通过设置环境变量来配置服务：

- `SERVER_URL`: 服务器地址，默认为 `http://127.0.0.1:5000`

## Docker 环境变量

在使用 Docker 部署时，可以通过以下环境变量进行配置：

- `SERVER_URL`: 服务器地址（必填）
- `TZ`: 时区，默认为 `Asia/Shanghai`

示例：
```bash
docker run -d \
  -p 5000:5000 \
  -e SERVER_URL=http://your-domain.com \
  -e TZ=Asia/Shanghai \
  --name yhjf \
  scp96/yhjf:latest
```

## 使用说明

1. 创建消息
   - 输入消息内容
   - 选择销毁方式（阅后即焚/定时销毁）
   - 可选择添加密码保护
   - 点击创建获取分享链接

2. 查看消息
   - 通过链接访问消息
   - 如有密码保护需输入密码
   - 阅后即焚消息查看一次后销毁
   - 定时销毁消息在到期后自动销毁

## 注意事项

- 密码错误超过3次，消息将被销毁
- 阅后即焚消息查看后无法再次查看
- 定时销毁消息在到期后自动删除
- 已删除的消息30天后物理删除
- 建议在生产环境中使用 HTTPS

## Docker Hub

项目 Docker 镜像托管在 [Docker Hub](https://hub.docker.com/r/scp96/yhjf)

## 开源协议

[MIT License](LICENSE)