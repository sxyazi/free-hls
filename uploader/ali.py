import requests

def handle(file):
  try:
    r = requests.post('https://kfupload.alibaba.com/mupload', data={
      'name': 'image.png',
      'scene': 'productImageRule'
    }, files={
      'file': ('image.png', open(file, 'rb'), 'image/png')
    }).json()

    return r['url']
  except:
    return None
