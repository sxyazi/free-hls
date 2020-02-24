import os, sys, glob, shutil, requests
from sys import argv
from utils import exec
from os import getenv as _
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
load_dotenv()
argv += [''] * 3

def publish(code, title=None):
  r = requests.post('%s/publish' % _('APIURL'), data={'code': code, 'title': title}).json()

  if r['code'] == 0:
    return '%s/play/%s' % (_('APIURL'), r['data'])
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

def bit_rate(file):
  return int(exec(['ffprobe','-v','error','-show_entries','format=bit_rate','-of','default=noprint_wrappers=1:nokey=1',file]))

def video_codec(file):
  codecs = exec(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=codec_name','-of','default=noprint_wrappers=1:nokey=1',file])
  return 'h264' if set(codecs.split('\n')).difference({'h264'}) else 'copy'

def command_generator(file):

  sub          = ''
  rate         = bit_rate(file)
  vcodec       = video_codec(file)
  segment_time = min(20, int((20 * 2 << 22) / (rate * 1.35)))


  #LIMITED
  if rate > 6e6 or argv[3] == 'LIMITED':
    br     = min(rate, 15e6)
    sub   += ' -b:v %d -maxrate %d -bufsize %d' % (br, 16e6, 16e6/1.5)
    vcodec, segment_time = 'h264', 5

  #SEGMENT_TIME
  if argv[3].isnumeric():
    sub += ' -segment_time %d' % float(argv[3])

  # return ' -i %s -codec copy -map 0 -f segment -segment_list out.m3u8 -segment_list_flags +live -segment_time 5 out%%03d.ts' % file
  # return ' -i %s -vcodec copy -acodec aac -hls_list_size 0 -hls_segment_size 3000000 -f hls out.m3u8' % file
  return ' -i %s -vcodec %s -acodec aac -map 0 -f segment -segment_list out.m3u8 %s out%%05d.ts' % (file, vcodec, sub)


def main():

  title   = argv[2] if len(argv)>2 else os.path.splitext(os.path.basename(argv[1]))[0]
  tmpdir  = os.path.dirname(os.path.abspath(__file__)) + '/tmp'
  command = command_generator(os.path.abspath(argv[1]))

  if os.path.isdir(tmpdir):
    shutil.rmtree(tmpdir)
  os.mkdir(tmpdir)
  os.chdir(tmpdir)
  print('ffmpeg %s' % command)
  os.system('ffmpeg %s' % command)

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
