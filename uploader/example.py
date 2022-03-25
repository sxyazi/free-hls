from os import getenv as _
from utils import session, upload_wrapper

# 上传驱动器类，类名不能改，一般一个驱动器对应一个网站的上传接口。编写完后，修改 .env 的 UPLOAD_DRIVE 为该驱动器的文件名，如“example.py”，则应该 UPLOAD_DRIVE=example
class Uploader:
  # 该上传驱动（即该网站）支持的最大文件大小，单位为字节。10 << 20 表示 10M
  MAX_BYTES = 10 << 20
  # 为了防止上传时检测文件内容格式，在文件前面填充的“图片头”，下面是 PNG 的文件头，按需要可以换成其它（比如 GIF），网上查一下就有了
  # 小技巧：能不伪造头就不伪造（很多网站是不检查上传“文件内容”的，只检查“文件名”）。如果要伪造，首选 PNG，GIF，因为这些格式一般不会被“有损压缩”，以确保上传后的视频数据不被损坏
  _BITS     = b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A\x00\x00\x00\x0D\x49\x48\x44\x52\x00' \
            + b'\x00\x00\x01\x00\x00\x00\x01\x08\x04\x00\x00\x00\xB5\x1C\x0C\x02\x00' \
            + b'\x00\x00\x0B\x49\x44\x41\x54\x78\x9C\x63\xFA\xCF\x00\x00\x02\x07\x01' \
            + b'\x02\x9A\x1C\x31\x71\x00\x00\x00\x00\x49\x45\x4E\x44\xAE\x42\x60\x82'

  @classmethod
  def params(cls):
    # 返回图片头的“填充长度”信息，因为在视频播放时，需要把图片头去掉，所以要知道你填充了多少字节在前面（件第23~25行）
    return {'padding': len(cls._BITS)} # 如果没填充，直接返回 {'padding': 0} 即可

  @classmethod
  @upload_wrapper
  def handle(cls, file):
    # （可选）给切片后的视频段，添加“图片头”，从而绕过某些网站对非图片文件的上传检测
    # 大部分网站都可以靠这个绕过，若不需要可以将下面一行注释。其实很多只检查文件名而已，因此只需要伪造文件名（见第31行）
    file = cls._BITS + file.read()

    try:
      # 上传图片 API 接口地址，通过浏览器抓包获得
      r = session.post('https://example.com/upload', files={
        # pic 是上传时的参数名，抓包获得
        'pic': ('image.png', file, 'image/png') # 某些网站只允许传 jpg，因此需要修改为：('image.jpg', file, 'image/jpeg')
      }, headers={
        # 有些网站需要登录才能上传，因此需要带 cookie
        # _('EXAMPLE_TOKEN') 指读取 .env 配置文件中的“EXAMPLE_TOKEN”变量，当然这个名字可以随便起
        'Cookie': 'token=%s' % _('EXAMPLE_TOKEN')
      }).json()

      # 检查上传结果，若成功，则返回图片地址
      return r['uploadInfo']['url'] # 上传后的图片地址
    except:
      # 上传失败，返回 None 就行了
      return None
