import os
import json
import time
import base64
import hashlib
from flask import Flask, request, jsonify, render_template, send_from_directory
app = Flask(__name__)

@app.route('/')
def hello():
  return 'Hello, World!'

@app.route('/play/<key>')
def play(key):
  file = 'userdata/%s' % key

  if not os.path.isfile(file):
    return jsonify({'code': -1, 'message': 'Key does not exist'})

  meta = json.load(open(file, 'r'))
  return render_template('play.html', meta=meta)

@app.route('/publish', methods=['POST'])
def publish():
  code = request.form.get('code')

  if not code:
    return jsonify({'code': -1, 'message': 'Code cannot be empty'})
  elif len(code) > 100*1024:
    return jsonify({'code': -1, 'message': 'Code size cannot exceed 100K'})

  key = filename(code)
  with open('userdata/%s' % key, 'w') as f:
    f.write(json.dumps({
      'code': base64.b64encode(code.encode('utf-8')).decode('ascii'),
      'title': request.form.get('title') or 'untitled',
      'created_at': int(time.time())
    }))

  return jsonify({'code': 0, 'data': key})


@app.route('/assets/<path:path>')
def send_js(path):
  return send_from_directory('assets', path)


def filename(code):
  md5 = hashlib.md5()
  md5.update(code.encode('utf-8'))
  return md5.hexdigest()


if __name__ == '__main__':
  app.run(host='127.0.0.1', port='3395', debug=True)
