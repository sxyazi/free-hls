import os, sys, requests
from sys import argv
from os import getenv as _
from uploader import Handler
from dotenv import load_dotenv
from utils import exec, tsfiles, safename, sameparams
from concurrent.futures import ThreadPoolExecutor, as_completed
load_dotenv()
argv += [''] * 3

def publish(code, title=None):
  try:
    r = requests.post('%s/publish' % _('APIURL'), data={'code': code, 'title': title}).json()
    if r['err']:
      print('Publish failed: %s' % r['message'])

    url = '%s/play/%s' % (_('APIURL'), r['data'])
    print('This video has been published to: %s' % url)
    print('You can also download it directly: %s.m3u8' % url)
  except:
    print('Publish failed: network connection error')

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

  return 'ffmpeg -i %s -vcodec %s -acodec aac -map 0 -f segment -segment_list out.m3u8 %s out%%05d.ts' % (safename(file), vcodec, sub)


def main():

  title   = argv[2] if argv[2] else os.path.splitext(os.path.basename(argv[1]))[0]
  tmpdir  = os.path.dirname(os.path.abspath(__file__)) + '/tmp'
  command = command_generator(os.path.abspath(argv[1]))

  if sameparams(tmpdir, command):
    os.chdir(tmpdir)
  else:
    os.mkdir(tmpdir)
    os.chdir(tmpdir)
    os.system(command)
    open('command.sh', 'w').write(command)

  failures, completions = 0, 0
  lines    = open('out.m3u8', 'r').read()
  executor = ThreadPoolExecutor(max_workers=10)
  futures  = {executor.submit(Handler, chunk): chunk for chunk in tsfiles(lines)}

  for future in as_completed(futures):
    completions += 1
    result = future.result()

    if not result:
      failures += 1
      print('[%s/%s] Uploaded failed: %s' % (completions, len(futures), futures[future]))
      continue

    lines = lines.replace(futures[future], result)
    print('[%s/%s] Uploaded %s to %s' % (completions, len(futures), futures[future], result))

  print('\n')

  #Write to file
  open('out.m3u8', 'w').write(lines)

  if not failures:
    publish(lines, title)
  else:
    print('Partially successful: %d/%d' % (completions, completions-failures))
    print('You can re-execute this program with the same parameters')



if __name__ == '__main__':
  main()
