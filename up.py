import os, re, json
from sys import argv
from os import getenv as _
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import api, exec, execstr, tsfiles, safename, uploader, sameparams
load_dotenv()
argv += [''] * 3

def checker(code):
  flag  = False
  limit = uploader().MAX_BYTES

  for file in tsfiles(code):
    if os.path.getsize(file) > limit:
      flag = True
      print('File too large: tmp/%s' % file)

  return exit(1) if flag else code

def encrypt(code):
  if not _('ENCRYPTION') == 'YES':
    return code

  for file in tsfiles(code):
    if file.startswith('enc.'):
      continue

    print('Encrypting %s to enc.%s ... ' % (file, file), end='')
    key = exec(['openssl','rand','16']).hex()
    iv  = execstr(['openssl','rand','-hex','16'])
    exec(['openssl','aes-128-cbc','-e','-in',file,'-out','enc.%s' % file,'-p','-nosalt','-iv',iv,'-K',key])

    key_id = api('POST', 'key', data={'iv': iv, 'key': key})
    if not key_id:
      print('failed')
      open('out.m3u8', 'w').write(code)
      exit()

    print('done')
    code = re.sub('(#EXTINF:.+$[\\r\\n]+^%s$)' % file, '#EXT-X-KEY:METHOD=AES-128,URI="%s/play/%s.key",IV=0x%s\n\\1' % (_('APIURL'), key_id, iv), code, 1, re.M)
    code = code.replace(file, 'enc.%s' % file)

  open('out.m3u8', 'w').write(code)
  return code

def publish(code, title=None):
  if _('NOSERVER') == 'YES':
    return print('The m3u8 file has been dumped to tmp/out.m3u8')

  r = api('POST', 'publish', data={'code': code, 'title': title,
                                   'params': json.dumps(uploader().params())})
  if r:
    url = '%s/play/%s' % (_('APIURL'), r)
    print('This video has been published to: %s' % url)
    print('You can also download it directly: %s.m3u8' % url)

def bit_rate(file):
  return int(execstr(['ffprobe','-v','error','-show_entries','format=bit_rate','-of','default=noprint_wrappers=1:nokey=1',file]))

def video_codec(file):
  codecs = execstr(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=codec_name','-of','default=noprint_wrappers=1:nokey=1',file])
  return 'h264' if set(codecs.split('\n')).difference({'h264'}) else 'copy'

def command_generator(file):

  sub          = ''
  rate         = bit_rate(file)
  vcodec       = video_codec(file)
  max_bits     = uploader().MAX_BYTES * 8
  segment_time = min(20, int(max_bits / (rate * 1.35)))


  #LIMITED
  if rate > 6e6 or argv[3] == 'LIMITED':
    maxrate = max_bits / 20 / 2.5
    sub    += ' -b:v %d -maxrate %d -bufsize %d' % (min(rate, maxrate*0.9), maxrate, maxrate/1.5)
    vcodec, segment_time = 'h264', 20

  #SEGMENT_TIME
  if argv[3].isnumeric():
    sub += ' -segment_time %d' % float(argv[3])
  else:
    sub += ' -segment_time %d' % segment_time

  return 'ffmpeg -i %s -vcodec %s -acodec aac -bsf:v h264_mp4toannexb -map 0:v:0 -map 0:a? -f segment -segment_list out.m3u8 %s out%%05d.ts' % (safename(file), vcodec, sub)


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
  lines    = checker(encrypt(open('out.m3u8', 'r').read()))
  executor = ThreadPoolExecutor(max_workers=10)
  futures  = {executor.submit(uploader().handle, chunk): chunk for chunk in tsfiles(lines)}

  for future in as_completed(futures):
    completions += 1
    result = future.result()

    if not result:
      failures += 1
      print('[%s/%s] Uploaded failed: %s' % (completions, len(futures), futures[future]))
      continue

    lines = lines.replace(futures[future], result)
    print('[%s/%s] Uploaded %s to %s' % (completions, len(futures), futures[future], result))

  #Write to file
  open('out.m3u8', 'w').write(lines)

  if not failures:
    publish(lines, title)
  else:
    print('Partially successful: %d/%d' % (completions, completions-failures))
    print('You can re-execute this program with the same parameters')



if __name__ == '__main__':
  main()
