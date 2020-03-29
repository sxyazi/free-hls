import os, tempfile, time
from os import getenv as _
from utils import uploader
from dotenv import load_dotenv
load_dotenv()

os.environ['UPLOAD_DRIVE'] = os.sys.argv[1]
handle, params = uploader().handle, uploader().params()

def upload(size):
  fd, path = tempfile.mkstemp()
  with open(path, 'wb') as f:
    f.write(os.urandom(size * 1048576 - params['padding']))

  r = handle(path)
  os.close(fd)
  os.unlink(path)
  return r

def test(curr, step):
  maps = {}
  reve = False
  reve_inc = None
  print('Starting test %s:' % _('UPLOAD_DRIVE'))

  while True:
    if curr in maps:
      result = maps[curr]
    else:
      result = maps[curr] = upload(curr)
      print('%dM\t%s\t%s' % (curr, 'OK' if result else 'FAIL', result))

    if not result:
      reve = True
    if not reve and curr > 20:
      step = 20
    if not reve and curr > 50:
      step = 30

    if not result and not reve_inc == None:
      print('\n---\nFinally ... %dM' % reve_inc)
      exit(0)

    if reve and result:
      reve_inc = curr
      curr += 1
    elif reve and not result:
      if (curr - 1) % 5 == 0:
        curr -= 1
      else:
        step //= 2
        curr -= max(1, step)
      if curr < 1:
        curr = 1
        reve_inc = 0
    elif not reve:
      curr += step


if __name__ == '__main__':

  # print(handle('/Users/ika/Desktop/test/9913509E9DE4492E0E903B4C2C66E98D.gif'))
  # print(handle('/Users/ika/Desktop/test/ACFC928140EE4FA072F4D6EB7CB35245.jpg'))
  # print(handle('/Users/ika/Desktop/test/out00006.ts'))

  test(1, 10)
