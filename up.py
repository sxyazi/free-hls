import os
import sys
import glob
import requests
from os import getenv as _
from shellescape import quote
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
load_dotenv()


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

  r = requests.post('https://www.yuque.com/api/upload/attach?attachable_id=%s&ctoken=%s' % (_('YUQUE_ATTACHID'), _('YUQUE_CTOKEN')), data={
    'type': 'attachment'
  }, files={
    'file': ('image.png', open(file, 'rb'), 'image/png')
  }, headers={
    'Referer': 'https://www.yuque.com/u85460/kb/hkvei2/edit',
    'Cookie': 'ctoken=%s; _yuque_session=%s' % (_('YUQUE_CTOKEN'), _('YUQUE_SESSION'))
  }).json()

  if 'data' in r and 'url' in r['data']:
    return r['data']['url']
  else:
    return None


def main():

  video = quote(os.path.abspath(sys.argv[1]))
  os.system('rm -rf /tmp/fmtmp; mkdir /tmp/fmtmp')
  os.chdir('/tmp/fmtmp')
  # os.system('/usr/local/bin/ffmpeg -i %s -codec copy -map 0 -f segment -segment_list out.m3u8 -segment_list_flags +live -segment_time 5 out%%03d.ts' % video)
  # os.system('/usr/local/bin/ffmpeg -i %s -vcodec copy -acodec aac -hls_list_size 0 -hls_segment_size 3000000 -f hls out.m3u8' % video)
  os.system('/usr/local/bin/ffmpeg -i %s -vcodec copy -acodec aac -map 0 -f segment -segment_list out.m3u8 -segment_time 20 out%%03d.ts' % video)

  i, lines = 0, open('out.m3u8', 'r').read()
  executor = ThreadPoolExecutor(max_workers=5)
  futures  = {executor.submit(upload_yuque, chunk): chunk for chunk in glob.glob('*.ts')}

  for future in as_completed(futures):
    lines = lines.replace(futures[future], future.result())

    i += 1
    print('[%s/%s] Uploaded %s to %s' % (i, len(futures), futures[future], future.result()))

  open('out.m3u8', 'w').write(lines)
  print('done')


if __name__ == '__main__':
  main()
