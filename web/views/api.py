import os
from . import app
from os import getenv as _
from utils import md5
from flask import request
from models import Video, Secret
from middleware import api_combined
from werkzeug.utils import secure_filename
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

  if 'file' not in request.files:
    return 0, 'No file part'

  file = request.files['file']
  if not file or file.filename == '':
    return 0, 'No selected file'

  name = secure_filename(file.filename)
  file.save(os.path.join('uploads', name))
  return 1, name

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
    slug = get('slug') or md5(get('code')))

@app.route('/paginate')
@api_combined
def paginate():
  pagination = PaginatedQuery(Video.select().order_by(Video.id.desc()), 50)

  return 1, {
    'pre': 50,
    'page': pagination.get_page(),
    'count': pagination.get_page_count(),
    'data': [model_to_dict(video) for video in pagination.get_object_list()]
  }
