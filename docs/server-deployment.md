# 其它部署方式

## Docker Compose

```bash
git clone https://github.com/sxyazi/free-hls.git && cd free-hls
docker-compose up -d
```

## 手动部署

安装最新的 Python3，以及必要包：

```bash
apt install -y python3 python3-pip
pip3 install Flask peewee gunicorn python-dotenv
```

启动服务

```bash
cd web
gunicorn app:app -b 0.0.0.0:3395 --workers=5 --threads=2 -D
```
