import os
import json
import time
import base64
import hashlib
from flask import Flask, Response, abort, request, jsonify, render_template, send_from_directory
app = Flask(__name__)

@app.route('/')
def hello():
  return 'Hello, World!'

@app.route('/favicon.ico')
def favicon():
  return abort(404)

@app.route('/play/<key>')
def play(key):
  file = 'userdata/%s' % os.path.splitext(key)[0]  #TODO

  if not os.path.isfile(file):
    return jsonify({'err': 1, 'message': 'Key does not exist'})

  meta = json.load(open(file, 'r'))
  if not key[-5:] == '.m3u8':
    return render_template('play.html', meta=meta)

  response = Response(meta['raw'], mimetype='application/vnd.apple.mpegurl')
  response.headers.add('Access-Control-Allow-Origin', '*')
  return response

@app.route('/publish', methods=['POST'])
def publish():
  code = request.form.get('code')

  if not code:
    return jsonify({'err': 1, 'message': 'Code cannot be empty'})
  elif len(code) > 100*1024:
    return jsonify({'err': 1, 'message': 'Code size cannot exceed 100K'})

  key = filename(code)
  with open('userdata/%s' % key, 'w') as f:
    f.write(json.dumps({
      'raw': code,
      'code': base64.b64encode(code.encode('utf-8')).decode('ascii'),
      'title': request.form.get('title') or 'untitled',
      'created_at': int(time.time())
    }))

  return jsonify({'err': 0, 'data': key})


@app.route('/assets/<path:path>')
def send_js(path):
  return send_from_directory('assets', path)


def filename(code):
  md5 = hashlib.md5(code.encode('utf-8')).hexdigest()
  return md5[8:24]


if __name__ == '__main__':
  app.run(host='127.0.0.1', port='3395', debug=True)
