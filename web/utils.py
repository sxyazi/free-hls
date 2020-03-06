import os
import json, time
import base64, hashlib

def filename(code):
  md5 = hashlib.md5(code.encode('utf-8')).hexdigest()
  return md5[8:24]

def readfile(skip=0):
  i, entities = 0, []

  try:
    with open('userdata/index') as f:
      for _ in range(skip):
        next(f)

      for line in f:
        if i >= 50:
          break

        i += 1
        entities.append(json.loads(line))
  except: pass
  return entities

def writefile(code, title=None):
  key  = filename(code)
  meta = {
    'key': key,
    'file': 'userdata/%s' % key,
    'title': title or 'untitled',
    'created_at': int(time.time())
  }

  if not os.path.isfile(meta['file']):
    with open('userdata/index', 'a') as f:
      f.write(json.dumps(meta) + '\n')

  with open(meta['file'], 'w') as f:
    meta['raw'] = code
    meta['code'] = base64.b64encode(code.encode('utf-8')).decode('ascii')
    f.write(json.dumps(meta))

  return key
