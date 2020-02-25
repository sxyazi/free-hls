import os, sys, glob, shutil, requests
from sys import argv
from os import getenv as _
from uploader import Handler
from dotenv import load_dotenv
from utils import exec, safename
from concurrent.futures import ThreadPoolExecutor, as_completed
load_dotenv()
argv += [''] * 3

def publish(code, title=None):
  r = requests.post('%s/publish' % _('APIURL'), data={'code': code, 'title': title}).json()

  if r['code'] == 0:
    return '%s/play/%s' % (_('APIURL'), r['data'])
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
  else:
    sub += ' -segment_time %d' % segment_time

  return ' -i %s -vcodec %s -acodec aac -map 0 -f segment -segment_list out.m3u8 %s out%%05d.ts' % (safename(file), vcodec, sub)


def main():

  title   = argv[2] if argv[2] else os.path.splitext(os.path.basename(argv[1]))[0]
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
  futures  = {executor.submit(Handler, chunk): chunk for chunk in glob.glob('*.ts')}

  for future in as_completed(futures):
    lines = lines.replace(futures[future], future.result())

    i += 1
    print('[%s/%s] Uploaded %s to %s' % (i, len(futures), futures[future], future.result()))

  url = publish(lines, title)
  print('\n')
  print('This video has been published to: %s' % url)
  print('You can also download it directly: %s.m3u8' % url)


if __name__ == '__main__':
  main()
