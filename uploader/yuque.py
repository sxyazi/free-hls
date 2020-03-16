from os import getenv as _
from utils import session, upload_wrapper

class Uploader:
  MAX_BYTES = 10 << 20

  @classmethod
  def params(cls):
    return {'padding': 0}

  @classmethod
  @upload_wrapper
  def handle(cls, file):
    try:
      r = session.post('https://www.yuque.com/api/upload/attach?ctoken=%s' % _('YUQUE_CTOKEN'), files={
        'file': ('image.png', file, 'image/png')
      }, headers={
        'Referer': 'https://www.yuque.com/yuque/topics/new',
        'Cookie': 'ctoken=%s; _yuque_session=%s' % (_('YUQUE_CTOKEN'), _('YUQUE_SESSION'))
      }).json()

      return r['data']['url']
    except:
      return None
