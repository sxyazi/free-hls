import os
import sys
import glob
import requests
from shellescape import quote
from concurrent.futures import ThreadPoolExecutor, as_completed




def upload(file):

  r = requests.post('https://kfupload.alibaba.com/mupload', data={
      'name': 'image.jpg',
      'scene': 'productImageRule'
  }, files={
      'file': ('image.jpg', open(file, 'rb'), 'image/jpeg')
  }).json()

  if 'url' in r:
    return r['url']
  else:
    return None


def main():

  video = quote(os.path.abspath(sys.argv[1]))
  os.system('rm -rf /tmp/fmtmp; mkdir /tmp/fmtmp')
  os.chdir('/tmp/fmtmp')
  # os.system('/usr/local/bin/ffmpeg -i %s -codec copy -map 0 -f segment -segment_list out.m3u8 -segment_list_flags +live -segment_time 5 out%%03d.ts' % video)
  # os.system('/usr/local/bin/ffmpeg -i %s -vcodec copy -acodec aac -hls_list_size 0 -hls_segment_size 3000000 -f hls out.m3u8' % video)
  os.system('/usr/local/bin/ffmpeg -i %s -vcodec copy -acodec aac -map 0 -f segment -segment_list out.m3u8 -segment_time 10 out%%03d.ts' % video)

  i, lines = 0, open('out.m3u8', 'r').read()
  executor = ThreadPoolExecutor(max_workers=5)
  futures  = {executor.submit(upload, chunk): chunk for chunk in glob.glob('*.ts')}

  for future in as_completed(futures):
    lines = lines.replace(futures[future], future.result())

    i += 1
    print('[%s/%s] Uploaded %s to %s' % (i, len(futures), futures[future], future.result()))

  open('out.m3u8', 'w').write(lines)
  print('done')


if __name__ == '__main__':
  main()
