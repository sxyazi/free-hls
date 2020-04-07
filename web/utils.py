import json, hashlib

def md5(s, short=False):
  md5 = hashlib.md5(s.encode('utf-8')).hexdigest()
  return md5[8:24] if short else md5

def validjson(s):
  try:
    json.loads(s)
    return True
  except:
    return False

def filtertags(s):
  return ','.join(list(dict.fromkeys(filter(None, s.split(','))))) if s else ''
