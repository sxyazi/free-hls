import os
import time, json, binascii
from dotenv import load_dotenv
from utils import readkey, writekey, listfile, readfile, writefile
from middleware import same_version, auth_required
from flask import (Flask, Response, abort, request, jsonify, 
                    render_template, send_from_directory)

load_dotenv()
app = Flask(__name__)

@app.route('/')
def hello():
  return 'Hello, World!'

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

  return jsonify({'err': 0, 'data': writekey(key, iv)})

@app.route('/play/<key>')
def play(key):
  real = os.path.splitext(key)[0]

  try:
    if key[-4:] == '.key':
      meta = readkey(real)
      r = Response(binascii.unhexlify(meta['key']), mimetype='application/octet-stream')
      r.headers.add('Access-Control-Allow-Origin', '*')
      return r

    meta = readfile(real)
    if key[-5:] == '.m3u8':
      r = Response(meta['raw'], mimetype='application/vnd.apple.mpegurl')
      r.headers.add('Access-Control-Allow-Origin', '*')
      return r

    return render_template('play.html', meta=meta)
  except:
    return jsonify({'err': 1, 'message': 'File does not exist'})

@app.route('/videos/<skip>', methods=['GET'])
@auth_required
@same_version
def videos(skip):
  try:
    skip = (int(skip) - 1) * 50
  except:
    skip = 0
  return jsonify({'err': 0, 'data': listfile(skip)})

@app.route('/publish', methods=['POST'])
@auth_required
@same_version
def publish():
  code = request.form.get('code')
  if not code:
    return jsonify({'err': 1, 'message': 'Code cannot be empty'})
  elif len(code) > 500*1024:
    return jsonify({'err': 1, 'message': 'Code size cannot exceed 500K'})

  key = writefile(code, request.form.get('title'))
  return jsonify({'err': 0, 'data': key})

@app.route('/assets/<path:path>')
def send_js(path):
  return send_from_directory('assets', path)


if __name__ == '__main__':
  app.run(host='127.0.0.1', port='3395', debug=True)
