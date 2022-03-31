# Free-HLS

这是一个免费的 HLS 视频解决方案，即所谓的视频床。本项目提供一整套集成化解决方案，囊括了各环节所需的切片、转码、上传、即时分享等套件。让您可以以更方便、更低廉的方式分享您的视频到任意地方。

本项目仅供学习交流使用，在使用过程中对您或他人造成的任何损失我们概不负责。

## 服务端

服务端位于项目的 `web` 目录，负责向客户端提供视频发布所必要的 API 接口，以及最终目标视频的播放服务。使用 Docker 快速部署它：

```bash
docker run --name free-hls -d -p 33950:3395 -v free-hls-data:/var/app sxyazi/free-hls
```

其它部署方式参见[其它部署方式](/docs/server-deployment.md)

## 客户端

客户端，即 `up.py` 入口，提供对上传视频资源的切片、转码、上传的支持。可以在您的任意机器上使用，只要您安装了必要的依赖项和作出了正确的配置。

### 1. 安装依赖

安装最新的 Python3，以及必要包：

```bash
apt install -y ffmpeg python3 python3-pip
pip3 install requests python-dotenv
```

### 2. 配置服务

复制客户端配置文件 `.env.example` 为 `.env`，修改其中的 `APIURL` 配置项为您的服务器域名或 IP 地址。将您的上传驱动器复制到 `uploader` 目录，并在 `.env` 中完成相应的配置。若没有驱动器，请参考 [上传驱动器](https://github.com/sxyazi/free-hls/wiki/%E4%B8%8A%E4%BC%A0%E9%A9%B1%E5%8A%A8%E5%99%A8)。

### 3. 开始使用

准备好目标视频文件，输入如下指令开始切片、上传：

```bash
python3 up.py test.mp4            #默认标题
python3 up.py test.mp4 测试标题    #自定义标题
python3 up.py test.mp4 测试标题 5  #自定义分段大小

python3 ls.py    #列出已上传视频
python3 ls.py 3  #列出已上传视频（第3页，50每页）
```

## 相似服务

- [https://github.com/sxzz/free-hls.js](https://github.com/sxzz/free-hls.js)
- [https://github.com/sxzz/free-hls-live](https://github.com/sxzz/free-hls-live)
- [https://github.com/MoeClub/Note/tree/master/ffmpeg](https://github.com/MoeClub/Note/tree/master/ffmpeg)
