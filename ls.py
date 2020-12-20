from sys import argv
from utils import api
from os import getenv as _
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
argv += [''] * 1

def main():
  try:
    page = int(argv[1])
  except:
    page = 1

  result = api('GET', 'paginate?page=%d' % page)
  for video in result['data']:
    link = '%s/play/%s' % (_('APIURL'), video['slug'])
    date = datetime.strptime(video['created_at'], '%a, %d %b %Y %H:%M:%S GMT')

    print('%s\t%s\t%s' % (video['title'], date, link))


if __name__ == '__main__':
  main()
