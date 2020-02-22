# Free-HLS

这是一个免费的 HLS 视频解决方案，即所谓的视频床。本项目提供一整套集成化解决方案，其中包括由 Python 编写的切片器、上传器。以及 PHP 编写的视频即时分享套件。在使用之前请先完成下面的两步配置。

本项目仅供学习交流使用，在使用过程中对你或他人造成的任何损失我们概不负责。



## 使用

安装最新的 Python3，以及必要包：

```bash
apt install -y ffmpeg python3 python3-pip
pip install shellescape python-dotenv
```

准备好目标视频文件，输入如下指令开始切片、上传：

```bash
python3 up.py test.mp4             #默认标题
python3 up.py test.mp4 我是测试视频  #自定义标题
```



## 配置语雀

将 `.env.example` 更名为 `.env`，修改其中的 `YUQUE_CTOKEN`、`YUQUE_SESSION` 配置。操作步骤：

1. 登录语雀 yuque.com；
2. 打开 Chrome 的开发者工具（Command+Shift+I），切换到 Network 面板；
3. 刷新页面，从 Cookie 中抓取 `ctoken`、`_yuque_session`，复制并替换到 `.env` 文件中；



## 配置 PHP 套件

安装最新的 PHP：

```bash
apt install -y php
```

使用 PHP 的 built-in WebServer 启动服务：

```bash
nohup php -S 0.0.0.0:3395 -t web > /dev/null 2>&1 &
```

文档只提供基础用法说明，有条件的同学可以自己装个 Nginx。完成上述后，修改 `.env` 文件中的 `APIURL` 为你的域名或 IP 地址。
