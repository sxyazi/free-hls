import os, sys, datetime
import time, threading, subprocess
from models import Video
from utils import md5, cloudconfig

def cloud():
  while True:
    time.sleep(3)
    video = Video.select().where(Video.status == 1).first()
    if not video: continue
    Video.update(status = 2).where(Video.id == video.id).execute()

    root = os.path.dirname(os.getcwd())
    envfile = cloudconfig()
    cmd = [sys.executable, f'{root}/up.py', '-c', envfile, f'{os.getcwd()}/queues/{video.id}']
    Video.update({Video.output: f'{" ".join(cmd)}\n'}).where(Video.id == video.id).execute()

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
      line = p.stdout.readline()
      if not line: break
      Video.update({Video.output: Video.output + line.decode('utf-8')}).where(Video.id == video.id).execute()

    p.wait()
    if p.returncode == 1:
      Video.update(status = 3).where(Video.id == video.id).execute()
    if p.returncode == 2:
      Video.update(status = 1).where(Video.id == video.id).execute()
    if p.returncode != 0:
      continue

    code = open(f'{root}/tmp/out.m3u8', 'r').read()
    Video.update(
      status = 0,
      code = code,
      slug = md5(code, True),
      params = open(f'{root}/tmp/params.json', 'r').read(),
      updated_at = datetime.datetime.now()
    ).where(Video.id == video.id).execute()



threading.Thread(target=cloud).start()
