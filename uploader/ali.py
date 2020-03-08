from utils import session

def handle(file):
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
