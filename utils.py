import os, re, glob, math
import requests, importlib
import shutil, hashlib, subprocess
from os import getenv as _
from functools import wraps
from constants import VERSION

def api(method, url, **kwargs):
  if method == 'POST':
    fn = requests.post
  else:
    fn = requests.get
  try:
    r = fn('%s/%s' % (_('APIURL'), url), **kwargs, headers={
      'API-Token': _('SECRET'),
      'API-Version': VERSION}).json()

    if not r['err']:
      return r['data']
    print('Request failed: %s' % r['message'])

  except:
    print('Request failed: connection error')

def md5(b):
  return hashlib.md5(b).hexdigest()

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
  return re.findall(r'^(?:enc\.)?(?:rep\.)?out\d+\.ts$', m3u8, re.M)

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
    with open(file, 'rb+') as g:
      return f(cls, g)

  return decorated

def bit_rate(file):
  return int(execstr(['ffprobe','-v','error','-show_entries','format=bit_rate','-of','default=noprint_wrappers=1:nokey=1',file]))

def maxbit_rate(file):
  name = os.path.splitext(file)[0]
  os.system('ffmpeg -y -i %s -c copy -map 0:v:0 -f segment -segment_time 1 -break_non_keyframes 1 %s.seg%%05d.ts' % (file, name))
  vrate = bit_rate(sorted(glob.glob('%s.seg*.ts' % name), key=os.path.getsize)[-1])

  list(map(os.remove, glob.glob('*.seg*.ts')))
  return vrate

def video_codec(file):
  codecs = execstr(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=codec_name','-of','default=noprint_wrappers=1:nokey=1',file])
  return 'h264' if set(codecs.split('\n')).difference({'h264'}) else 'copy'

def video_duration(file):
  return float(execstr(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',file]))

def genslice(file, time):
  sub          = ''
  rate         = bit_rate(file)
  vcodec       = video_codec(file)
  max_bits     = uploader().MAX_BYTES * 8
  segment_time = min(20, int(max_bits / (rate * 1.35)))

  #SEGMENT_TIME
  sub += ' -segment_time %d' % (time or segment_time)

  return 'ffmpeg -y -i %s -vcodec %s -acodec aac -bsf:v h264_mp4toannexb -map 0:v:0 -map 0:a? -f segment -segment_list out.m3u8 %s out%%05d.ts' % (safename(file), vcodec, sub)

def genrepair(file, newfile, maxbits):
  maxrate = maxbits / math.ceil(video_duration(file)) / max(1, maxbit_rate(file) / bit_rate(file))
  return 'ffmpeg -y -i %s -copyts -vsync 0 -muxdelay 0 -vcodec h264 -acodec copy -bsf:v h264_mp4toannexb -b:v %s -maxrate %s -bufsize %s %s' % (file, maxrate*0.9, maxrate, maxrate*1.5, newfile)


session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Mobile/11A465 QQLiveBrowser/7.0.8 WebKitCore/UIWebView'})
