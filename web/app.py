import os
import time, json
from dotenv import load_dotenv
from utils import readfile, writefile
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

@app.route('/videos/<skip>', methods=['GET'])
@auth_required
@same_version
def videos(skip):
  try:
    skip = (int(skip) - 1) * 50
  except:
    skip = 0
  return jsonify({'err': 0, 'data': readfile(skip)})

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
