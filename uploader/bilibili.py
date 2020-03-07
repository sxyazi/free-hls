import requests
from os import getenv as _

def handle(file):
  try:
    r = requests.post('https://api.vc.bilibili.com/api/v1/drawImage/upload', data={
        'category': 'daily'
    }, files={
      'file_up': ('image.gif', b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A' + open(file, 'rb').read(), 'image/gif')
    }, headers={
      'Cookie': 'SESSDATA=%s' % _('BILIBILI_SESSDATA')
    }).json()

    return r['data']['image_url']
  except:
    return None
