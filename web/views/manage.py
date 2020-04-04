from . import app
from models import Video
from middleware import api_combined
from flask import request, render_template

@app.route('/post', methods=['GET'])
def post():
  return render_template('post.html')
