# Free-HLS

这是一个免费的 HLS 视频解决方案，即所谓的视频床。本项目提供一整套集成化解决方案，囊括了各环节所需的切片、转码、上传、即时分享等套件。让你可以以更方便、更低廉的方式分享你的视频到任意地方。

本项目仅供学习交流使用，在使用过程中对你或他人造成的任何损失我们概不负责。

**视频教程：只需 10 分钟搭建出一款属于自己的视频床：[https://sxyz.gitee.io/free-hls/usage.html](https://sxyz.gitee.io/free-hls/usage.html)**



## 客户端

客户端，即 `up.py` 入口，提供对上传视频资源的切片、转码、上传的支持。可以在你的任意机器上使用，只要你安装了必要的依赖项和作出了正确的配置。

### 1. 安装依赖

安装最新的 Python3，以及必要包：

```bash
apt install -y ffmpeg python3 python3-pip
pip3 install requests python-dotenv
```



### 2. 配置语雀

将 `.env.example` 更名为 `.env`，修改其中的 `YUQUE_CTOKEN`、`YUQUE_SESSION` 配置。操作步骤：

1. 登录语雀 yuque.com；
2. 打开 Chrome 的开发者工具（Command+Shift+I），切换到 Network 面板；
3. 刷新页面，从 Cookie 中抓取 `ctoken`、`_yuque_session`，复制并替换到 `.env` 文件中；



### 3. 配置服务

正确施行 [服务端](#服务端) 一节的全部内容，完成服务端的搭建。将你服务器的域名或 IP 地址修改到 `.env` 中的  `APIURL` 配置项。



### 4. 开始使用

准备好目标视频文件，输入如下指令开始切片、上传：

```bash
python3 up.py test.mp4               #默认标题
python3 up.py test.mp4 测试哦         #自定义标题
python3 up.py test.mp4 test 5        #自定义分段大小
python3 up.py test.mp4 test LIMITED  #限制码率（需重编码）
```



## 服务端

服务端位于项目的 `web` 目录，负责向客户端提供视频发布所必要的 API 接口。以及最终目标视频的播放服务。

### 1. 安装依赖

安装最新的 Python3，以及必要包：

```bash
apt install -y python3 python3-pip
pip3 install Flask gunicorn
```



### 2. 启动服务

```bash
cd web
gunicorn app:app -b 0.0.0.0:3395 -D
```


## 相似服务

- [https://github.com/sxzz/free-hls.js](https://github.com/sxzz/free-hls.js)
- [https://github.com/sxzz/free-hls-live](https://github.com/sxzz/free-hls-live)
- [https://github.com/MoeClub/Note/tree/master/ffmpeg](https://github.com/MoeClub/Note/tree/master/ffmpeg)
