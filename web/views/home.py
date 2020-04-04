import os
import binascii
from . import app
from models import Video, Secret
from flask import abort, jsonify, Response, render_template

@app.route('/')
def home():
  return render_template('home.html')
  # return 'Hello, Free-HLS!'

@app.route('/play/<slug>')
def play(slug):
  real = os.path.splitext(slug)[0]

  try:
    if slug[-4:] == '.key':
      secret = Secret.get_by_id(real)
      r = Response(binascii.unhexlify(secret.key), mimetype='application/octet-stream')
      r.headers.add('Access-Control-Allow-Origin', '*')
      return r

    video = Video.get(Video.slug == real)
    if slug[-5:] == '.m3u8':
      r = Response(video.code, mimetype='application/vnd.apple.mpegurl')
      r.headers.add('Access-Control-Allow-Origin', '*')
      return r

    return render_template('play.html', video=video)
  except:
    return jsonify({'err': 1, 'message': 'Resource does not exist'})
