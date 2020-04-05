from . import app
from models import Tag, Video
from flask import request, render_template
from playhouse.shortcuts import model_to_dict
from middleware import api_response, api_combined

@app.route('/tag')
@app.route('/tag/<id>')
def tag():
  return 1,1

@app.route('/tags')
@api_response
def tags():
  if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    q = '%%%s%%' % request.args['q']
    return 1, [model_to_dict(tag) for tag in Tag.select().where(Tag.name ** q).limit(10)]

  return render_template('tags.html')


@app.route('/video')
@app.route('/video/<id>')
def video(id = 0):
  video = Video.get_by_id(id) if id else {}
  return render_template('video.html', video=video)

@app.route('/videos')
def videos():
  return render_template('videos.html')
