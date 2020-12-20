import os
import shutil
import tempfile
from sys import argv
from dotenv import load_dotenv
from utils import exec, uploader, genrepair, bit_rate, maxbit_rate, video_duration
load_dotenv()


def main():
  d = tempfile.mkdtemp()
  os.chdir(d)

  name = 'video%s' % os.path.splitext(argv[1])[1]
  shutil.copyfile(argv[1], name)

  bitrate = bit_rate(name)
  maxbitrate = maxbit_rate(name)
  duration = video_duration(name)
  repaircmd = genrepair(name, name, uploader().MAX_BYTES)
  os.system('clear')

  print('\n=================================')
  print('file: %s' % argv[1])
  print('size: %s' % os.path.getsize(name))
  print('bitrate: %s' % bitrate)
  print('max_bitrate: %s' % maxbitrate)
  print('duration: %s' % duration)
  print('genrepair: %s' % repaircmd)
  print('=================================\n')

  exec(['rm', '-rf', d])


if __name__ == '__main__':
  main()
