from . import app
from flask import abort, make_response, send_from_directory

@app.route('/favicon.ico')
def favicon():
  return abort(404)

@app.route('/assets/<path:path>')
def send_js(path):
  return send_from_directory('assets', path)

@app.route('/uploads/<path:path>')
def send_file(path):
  r = make_response(send_from_directory('uploads', path))
  r.headers.add('Access-Control-Allow-Origin', '*')
  return r
