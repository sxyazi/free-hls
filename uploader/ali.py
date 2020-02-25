import requests

def upload_ali(file):

  r = requests.post('https://kfupload.alibaba.com/mupload', data={
    'name': 'image.png',
    'scene': 'productImageRule'
  }, files={
    'file': ('image.png', open(file, 'rb'), 'image/png')
  }).json()

  if 'url' in r:
    return r['url']
  else:
    return None
