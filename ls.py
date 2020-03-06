import time
from sys import argv
from utils import api
from os import getenv as _
from dotenv import load_dotenv
load_dotenv()
argv += [''] * 1

def main():
  try:
    skip = int(argv[1])
  except:
    skip = 0

  for video in api('GET', 'videos/%d' % skip):
    link = '%s/play/%s' % (_('APIURL'), video['key'])
    date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(video['created_at']))

    print('%s\t%s\t%s' % (video['title'], date, link))


if __name__ == '__main__':
  main()
