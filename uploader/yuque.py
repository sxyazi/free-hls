from utils import session
from os import getenv as _

def handle(file):
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
