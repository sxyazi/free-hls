from utils import session, upload_wrapper

class Uploader:
  MAX_BYTES = 5 << 20

  @classmethod
  def params(cls):
    return {'padding': 0}

  @classmethod
  @upload_wrapper
  def handle(cls, file):
    try:
      r = session.post('https://kfupload.alibaba.com/mupload', data={
        'name': 'image.png',
        'scene': 'productImageRule'
      }, files={
        'file': ('image.png', file, 'image/png')
      }).json()

      return r['url']
    except:
      return None
