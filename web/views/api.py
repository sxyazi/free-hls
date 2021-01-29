import os
from . import app
from os import getenv as _
from flask import request
from models import Video, Secret
from middleware import api_combined
from utils import md5, saveupload
from playhouse.shortcuts import model_to_dict
from playhouse.flask_utils import PaginatedQuery

@app.route('/key', methods=['POST'])
@api_combined
def key():
  iv  = request.form.get('iv')
  key = request.form.get('key')

  if len(iv) != 32 or len(key) != 32:
    return 0, 'Invalid key or iv'

  return Secret.add(iv, key)

@app.route('/upload', methods=['POST'])
@api_combined
def upload():
  if not _('ENABLE_UPLOAD') == 'YES':
    return 0, 'Upload is not enabled'
  return saveupload('uploads')

@app.route('/queue', methods=['POST'])
@api_combined
def queue():
  ok, file = saveupload('queues', True)
  if not ok:
    return 0, file

  video = Video.add(
    status = 1,
    params = '{}',
    tags = request.form.get('tags'),
    title = request.form.get('title'))

  os.rename(file, f'{os.path.dirname(file)}/{video.id}')
  return 1, video.id

@app.route('/publish', methods=['POST'])
@api_combined
def publish():
  get = request.form.get

  return Video.createOrUpdate(
    id = get('id'),
    code = get('code'),
    tags = get('tags'),
    title = get('title'),
    params = get('params'),
    slug = get('slug') or md5(get('code'), True))

@app.route('/paginate')
@api_combined
def paginate():
  pagination = PaginatedQuery(Video.select().order_by(Video.id.desc()), 50)

  return 1, {
    'pre': 50,
    'page': pagination.get_page(),
    'count': Video.select().count(),
    'data': [{**model_to_dict(video), 'code': None} for video in pagination.get_object_list()]
  }
