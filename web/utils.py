import json, hashlib

def md5(s):
  md5 = hashlib.md5(s.encode('utf-8')).hexdigest()
  return md5[8:24]

def validjson(s):
  try:
    json.loads(s)
    return True
  except:
    return False
