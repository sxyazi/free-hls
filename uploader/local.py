from os import getenv as _
from utils import api, md5, upload_wrapper

class Uploader:
  MAX_BYTES = 20 << 20

  @classmethod
  def params(cls):
    return {'padding': 0}

  @classmethod
  @upload_wrapper
  def handle(cls, file):
    file = file.read()
    r = api('POST', 'upload', files={
      'file': ('%s.ts' % md5(file), file, 'video/mp2t')
    })

    if not r:
      return None

    return '%s/uploads/%s' % (_('APIURL'), r)
