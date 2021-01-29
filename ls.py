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

  result = api('GET', f'paginate?page={page}')
  for video in result['data']:
    link = f'{_("APIURL")}/play/{video["slug"]}'
    date = datetime.strptime(video['created_at'], '%a, %d %b %Y %H:%M:%S GMT')

    print(f'{video["title"]}\t{date}\t{link}')


if __name__ == '__main__':
  main()
