import os, json, shutil, hashlib
from os import path
from flask import request
from werkzeug.utils import secure_filename

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

def saveupload(dir, full=False):
  if 'file' not in request.files:
    return 0, 'No file part'

  file = request.files['file']
  if not file or file.filename == '':
    return 0, 'No selected file'

  path = os.path.join(dir, secure_filename(file.filename))
  file.save(path)
  return 1, path if full else os.path.basename(path)

def cloudconfig():
  root = path.dirname(path.dirname(path.abspath(__file__)))
  config = f'{root}/.env.cloud'
  shutil.copy(f'{root}/.env', config)

  with open(config, 'a') as f:
    f.write('\n')
    f.write('\n')
    f.write('NOSERVER=YES\n')

  return config
