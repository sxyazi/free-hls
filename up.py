import argparse
import os, re, json
from os import path
from os import getenv as _
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import (api, exec, execstr, tsfiles, uploader,
                    manageurl, sameparams, genslice, genrepair)

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
      open('out.m3u8', 'w').write(code)
      print('failed')
      exit(1)

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
    url = '%s/play/%s' % (_('APIURL'), r['slug'])
    print('This video has been published to: %s' % url)
    print('You can also download it directly: %s.m3u8' % url)
    print('---')
    print('Click here to edit the information for this video:\n%s' % manageurl('video/%s' % r['id']))

def repairer(code):
  limit = uploader().MAX_BYTES

  for file in tsfiles(code):
    if path.getsize(file) > limit:
      tmp = 'rep.%s' % file
      os.system(genrepair(file, tmp, limit * 8))
      os.rename(tmp, file)

      if path.getsize(file) > limit:
        open('out.m3u8', 'w').write(code)
        print('File too large: tmp/%s' % file)
        print('Adjust parameters or continue execution with the same parameters')
        exit(1)

  open('out.m3u8', 'w').write(code)
  return code


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('file', type=str, help='video file')
  parser.add_argument('title', type=str, nargs='?', help='post title')
  parser.add_argument('time', type=int, nargs='?', help='time for pre segment', default=0)
  parser.add_argument('-c, --config', type=str, dest='config', help='change the configuration file path')
  args = parser.parse_args()

  load_dotenv(args.config)
  tmpdir  = path.dirname(path.abspath(__file__)) + '/tmp'
  command = genslice(path.abspath(args.file), args.time)

  if sameparams(tmpdir, command):
    os.chdir(tmpdir)
  else:
    os.mkdir(tmpdir)
    os.chdir(tmpdir)
    os.system(command)
    open('command.sh', 'w').write(command)

  failures, completions = 0, 0
  lines    = encrypt(repairer(open('out.m3u8', 'r').read()))
  executor = ThreadPoolExecutor(max_workers=15)
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
  open('params.json', 'w').write(json.dumps(uploader().params()))

  if not failures:
    publish(lines, args.title or path.splitext(path.basename(args.file))[0])
  else:
    print('Partially successful: %d/%d' % (completions-failures, completions))
    print('You can re-execute this program with the same parameters')



if __name__ == '__main__':
  main()
