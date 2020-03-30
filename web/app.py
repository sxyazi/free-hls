import os
import time, json, binascii
from os import getenv as _
from dotenv import load_dotenv
from model import Video, Secret
from utils import md5, validjson
from werkzeug.utils import secure_filename
from playhouse.shortcuts import model_to_dict
from middleware import same_version, auth_required
from flask import (Flask, Response, abort, request, jsonify,
                    make_response, render_template, send_from_directory)

load_dotenv()
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 << 20

@app.route('/')
def hello():
  return 'Hello, Free-HLS!'

@app.route('/favicon.ico')
def favicon():
  return abort(404)

@app.route('/key', methods=['POST'])
@auth_required
@same_version
def key():
  iv  = request.form.get('iv')
  key = request.form.get('key')

  if len(iv) != 32 or len(key) != 32:
    return jsonify({'err': 1, 'message': 'Invalid key or iv'})

  secret = Secret.create(iv=iv, key=key)
  return jsonify({'err': 0, 'data': secret.id})

@app.route('/play/<key>')
def play(key):
  real = os.path.splitext(key)[0]

  try:
    if key[-4:] == '.key':
      secret = Secret.get_by_id(real)
      r = Response(binascii.unhexlify(secret.key), mimetype='application/octet-stream')
      r.headers.add('Access-Control-Allow-Origin', '*')
      return r

    video = Video.get(Video.key == real)
    if key[-5:] == '.m3u8':
      r = Response(video.code, mimetype='application/vnd.apple.mpegurl')
      r.headers.add('Access-Control-Allow-Origin', '*')
      return r

    return render_template('play.html', video=video)
  except:
    return jsonify({'err': 1, 'message': 'Resource does not exist'})

@app.route('/videos/<page>', methods=['GET'])
@auth_required
@same_version
def videos(page):
  try:
    page = int(page)
  except:
    page = 1

  pagination = Video.select(Video.key, Video.title, Video.created_at).order_by(Video.id).paginate(page, 50)
  return jsonify({'err': 0, 'data': [model_to_dict(video) for video in pagination]})

@app.route('/upload', methods=['POST'])
@auth_required
@same_version
def upload():
  if not _('ENABLE_UPLOAD') == 'YES':
    return jsonify({'err': 1, 'message': 'Upload is not enabled'})

  if 'file' not in request.files:
    return jsonify({'err': 1, 'message': 'No file part'})

  file = request.files['file']
  if not file or file.filename == '':
    return jsonify({'err': 1, 'message': 'No selected file'})

  name = secure_filename(file.filename)
  file.save(os.path.join('uploads', name))
  return jsonify({'err': 0, 'data': name})

@app.route('/publish', methods=['POST'])
@auth_required
@same_version
def publish():
  code = request.form.get('code')
  params = request.form.get('params')
  if not code:
    return jsonify({'err': 1, 'message': 'Code cannot be empty'})
  elif len(code) > 500*1024:
    return jsonify({'err': 1, 'message': 'Code size cannot exceed 500K'})
  elif not validjson(params):
    return jsonify({'err': 1, 'message': 'Invalid params'})

  key = md5(code)
  Video.replace(key = key, code = code, params = params, title = request.form.get('title')).execute()
  return jsonify({'err': 0, 'data': key})

@app.route('/assets/<path:path>')
def send_js(path):
  return send_from_directory('assets', path)

@app.route('/uploads/<path:path>')
def send_file(path):
  r = make_response(send_from_directory('uploads', path))
  r.headers.add('Access-Control-Allow-Origin', '*')
  return r


if __name__ == '__main__':
  app.run(host='0.0.0.0', port='3395', debug=True)
