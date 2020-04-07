import os
import binascii
from . import app
from models import Tag, Video, Secret, VideoTag
from flask import abort, jsonify, request, Response, render_template

@app.route('/')
def home():
  total_tags = Tag.select().count()
  total_videos = Video.select().count()
  latest_tags = {vtag.tag.id: vtag.tag for vtag in VideoTag.select().join(Tag).order_by(VideoTag.id.desc()).group_by(VideoTag.tag).limit(10)}
  video_tags = VideoTag.select().join(Tag).switch(VideoTag).join(Video).where(VideoTag.tag << list(latest_tags)).order_by(VideoTag.id.desc()).limit(50)

  tags_videos = {}
  for vt in video_tags:
    if vt.tag.id not in tags_videos:
      tags_videos[vt.tag.id] = []
    tags_videos[vt.tag.id].append(vt.video)

  return render_template('home.html', total_tags=total_tags, total_videos=total_videos, 
    latest_tags=latest_tags, tags_videos=tags_videos)

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

    return render_template('play.html', video=video, notitle=request.args.get('notitle'))
  except:
    return jsonify({'err': 1, 'message': 'Resource does not exist'})

@app.route('/playlist/<tag_id>')
def playlist(tag_id):
  tag = Tag.get_by_id(tag_id)
  videos = VideoTag.blend(tag)
  watch = request.args.get('watch') or videos[0]['slug']

  return render_template('playlist.html', tag=tag, watch=watch, videos=videos)
