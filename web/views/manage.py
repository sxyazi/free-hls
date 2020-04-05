from . import app
from models import Tag, Video
from flask import request, render_template
from playhouse.shortcuts import model_to_dict
from playhouse.flask_utils import PaginatedQuery
from middleware import api_response, api_combined

@app.route('/tag', methods=['GET', 'POST'])
@app.route('/tag/<id>', methods=['GET', 'POST'])
def tag(id = 0):
  pass

@app.route('/tags')
@api_response
def tags():
  if 'q' in request.args:
    q = '%%%s%%' % request.args['q']
    return 1, [model_to_dict(tag) for tag in Tag.select().where(Tag.name ** q).limit(10)]

  if 'list' in request.args:
    pagination = PaginatedQuery(Tag.select().order_by(Tag.id.desc()), 50)
    return 1, {
      'pre': 50,
      'page': pagination.get_page(),
      'count': Tag.select().count(),
      'data': [model_to_dict(video) for video in pagination.get_object_list()]
    }

  return render_template('tags.html')


@app.route('/video', methods=['GET', 'POST'])
@app.route('/video/<id>', methods=['GET', 'POST'])
@api_response
def video(id = 0):
  if 'remove' in request.form:
    return Video.remove(id)

  video = Video.get_by_id(id) if id else {}
  return render_template('video.html', video=video)

@app.route('/videos')
def videos():
  return render_template('videos.html')
