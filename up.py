import os
import sys
import glob
import shutil
import requests
import subprocess
from os import getenv as _
from shellescape import quote
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
load_dotenv()

def publish(code, title=None):
  r = requests.post('%s/publish.php' % _('APIURL'), data={
    'code': code,
    'title': title
  }).json()

  if r['code'] == 0:
    return r['data']['url']
  else:
    return None

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

def upload_yuque(file):

  r = requests.post('https://www.yuque.com/api/upload/attach?ctoken=%s' % _('YUQUE_CTOKEN'), files={
    'file': ('image.png', open(file, 'rb'), 'image/png')
  }, headers={
    'Referer': 'https://www.yuque.com/yuque/topics/new',
    'Cookie': 'ctoken=%s; _yuque_session=%s' % (_('YUQUE_CTOKEN'), _('YUQUE_SESSION'))
  }).json()

  if 'data' in r and 'url' in r['data']:
    return r['data']['url']
  else:
    return None

def segment_time(file):
  rate = os.popen('ffprobe -v error -show_entries format=bit_rate -of default=noprint_wrappers=1:nokey=1 %s' % file).read().strip()

  try:
    return int((20 * 2 << 22) / (int(rate) * 1.35))
  except Exception:
    return 10

def video_codec(file):
  codecs = os.popen('ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 %s' % file).read().strip()

  s = set(codecs.split('\n'))
  return 'copy' if 'h264' in s and len(s) == 1 else 'h264'

def main():

  video  = quote(os.path.abspath(sys.argv[1]))
  title  = sys.argv[2] if len(sys.argv)>2 else os.path.splitext(os.path.basename(sys.argv[1]))[0]
  stime  = float(sys.argv[3]) if len(sys.argv)>3 else segment_time(video)
  vcodec = video_codec(video)
  tmpdir = os.path.dirname(os.path.abspath(__file__)) + '/tmp'

  if os.path.isdir(tmpdir):
    shutil.rmtree(tmpdir)
  os.mkdir(tmpdir)
  os.chdir(tmpdir)

  # os.system('ffmpeg -i %s -codec copy -map 0 -f segment -segment_list out.m3u8 -segment_list_flags +live -segment_time 5 out%%03d.ts' % video)
  # os.system('ffmpeg -i %s -vcodec copy -acodec aac -hls_list_size 0 -hls_segment_size 3000000 -f hls out.m3u8' % video)
  os.system('ffmpeg -i %s -vcodec %s -acodec aac -map 0 -f segment -segment_list out.m3u8 -segment_time %d out%%03d.ts' % (video, vcodec, stime))

  i, lines = 0, open('out.m3u8', 'r').read()
  executor = ThreadPoolExecutor(max_workers=10)
  futures  = {executor.submit(upload_yuque, chunk): chunk for chunk in glob.glob('*.ts')}

  for future in as_completed(futures):
    lines = lines.replace(futures[future], future.result())

    i += 1
    print('[%s/%s] Uploaded %s to %s' % (i, len(futures), futures[future], future.result()))

  print('This video has been published to: %s' % publish(lines, title))


if __name__ == '__main__':
  main()
