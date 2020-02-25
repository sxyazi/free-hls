import os
import re
import shutil
import subprocess

def exec(cmd, timeout=None, **kwargs):
  p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

  communicate_kwargs = {}
  if timeout is not None:
    communicate_kwargs['timeout'] = timeout

  out, err = p.communicate(**communicate_kwargs)
  if p.returncode != 0:
    raise Exception(cmd, out, err.decode('utf-8'))

  return out.decode('utf-8').strip()

def tsfiles(m3u8):
  return re.findall(r'^out\d+\.ts$', m3u8, re.M)

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
