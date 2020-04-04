import os
from . import app
from os import getenv as _
from flask import request
from models import Video, Secret
from middleware import api_combined
from werkzeug.utils import secure_filename
from playhouse.shortcuts import model_to_dict

@app.route('/key', methods=['POST'])
@api_combined
def key():
  iv  = request.form.get('iv')
  key = request.form.get('key')

  if len(iv) != 32 or len(key) != 32:
    return 0, 'Invalid key or iv'

  return Secret.add(iv, key)

@app.route('/videos/<page>', methods=['GET'])
@api_combined
def videos(page):
  try:
    page = int(page)
  except:
    page = 1

  pagination = Video.select(Video.key, Video.title, Video.created_at).order_by(Video.id).paginate(page, 50)
  return 1, [model_to_dict(video) for video in pagination]

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
  return Video.save(get('code'), get('title'), get('params'))
