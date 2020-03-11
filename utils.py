import os, re
import shutil
import requests
import importlib
import subprocess
from os import getenv as _
from functools import wraps
from constants import VERSION

def api(method, url, data=None):
  if method == 'POST':
    fn = requests.post
  else:
    fn = requests.get
  try:
    r = fn('%s/%s' % (_('APIURL'), url), data=data, headers={
      'API-Token': _('SECRET'),
      'API-Version': VERSION}).json()

    if not r['err']:
      return r['data']
    print('Request failed: %s' % r['message'])

  except:
    print('Request failed: connection error')

def exec(cmd, timeout=None, **kwargs):
  p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

  communicate_kwargs = {}
  if timeout is not None:
    communicate_kwargs['timeout'] = timeout

  out, err = p.communicate(**communicate_kwargs)
  if p.returncode != 0:
    raise Exception(cmd, out, err.decode('utf-8'))

  return out

def execstr(*args, **kwargs):
  return exec(*args, **kwargs).decode('utf-8').strip()

def tsfiles(m3u8):
  return re.findall(r'^(?:enc\.)?out\d+\.ts$', m3u8, re.M)

def safename(file):
  return '"' + file.replace('"', '\\"') + '"'

def sameparams(dir, command):
  if not os.path.isdir(dir):
    return False

  try:
    if open('%s/command.sh' % dir, 'r').read() != command:
      shutil.rmtree(dir)
      return False
  except:
    shutil.rmtree(dir)
    return False

  return True

def uploader():
  return importlib.import_module('uploader.' + _('UPLOAD_DRIVE')).Uploader

def upload_wrapper(f):
  @wraps(f)
  def decorated(cls, file):
    with open(file, 'rb') as g:
      return f(cls, g)

  return decorated


session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Mobile/11A465 QQLiveBrowser/7.0.8 WebKitCore/UIWebView'})
