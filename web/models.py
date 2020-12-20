import datetime
from peewee import *
from utils import md5, validjson, filtertags
from playhouse.shortcuts import model_to_dict
db = SqliteDatabase('data.db', pragmas={'foreign_keys': 1})

class Video(Model):
  slug = CharField(unique=True, null=True)
  code = TextField(default='')
  tags = CharField()
  title = CharField()
  params = TextField()
  output = TextField(default='')
  # 0.已发布， 1.队列中，2.处理中，3.发布失败
  status = IntegerField(default=0, index=True)
  created_at = DateTimeField(default=datetime.datetime.now)
  updated_at = DateTimeField(null=True)

  class Meta:
    database = db
    db_table = 'videos'

  @classmethod
  def add(cls, **kwargs):
    kwargs['tags'] = filtertags(kwargs['tags']) or '未标记'
    with db.atomic():
      video = cls.create(**kwargs)
      Tag.add(kwargs['tags'], video.id)
    return video

  @classmethod
  def remove(cls, id):
    with db.atomic():
      for tag in VideoTag.tags(id):
        Tag.unlink(tag, id)

      cls.delete().where(cls.id == id).execute()

    return 1, id

  @classmethod
  def createOrUpdate(cls, **kwargs):
    if not kwargs['slug']:
      return 0, 'Slug cannot be empty'
    if not kwargs['code']:
      return 0, 'Code cannot be empty'
    elif len(kwargs['code']) > 500*1024:
      return 0, 'Code size cannot exceed 500K'
    elif not validjson(kwargs['params']):
      return 0, 'Invalid params'
    kwargs['tags'] = filtertags(kwargs['tags']) or '未标记'

    with db.atomic():
      id = kwargs.pop('id') if 'id' in kwargs else 0
      if id:
        cls.update(**kwargs).where(cls.id == id).execute()
        video = cls.get_by_id(id)
      elif cls.select().where(cls.slug == kwargs['slug']).exists():
        cls.update(**kwargs).where(cls.slug == kwargs['slug']).execute()
        video = cls.get(cls.slug == kwargs['slug'])
      else:
        video = cls.create(**kwargs)
      Tag.add(kwargs['tags'], video.id)

    return 1, model_to_dict(video)


class Tag(Model):
  name = CharField(unique=True)
  created_at = DateTimeField(default=datetime.datetime.now)

  class Meta:
    database = db
    db_table = 'tags'

  @classmethod
  def add(cls, tags, video_id):
    tags       = tags.split(',') if tags else []
    all_tags   = [tag.name for tag in cls.select().where(cls.name << tags)]
    video_tags = [tag.name for tag in VideoTag.tags(video_id)]

    for tag in set(tags) - set(all_tags):
      cls.create(name = tag)
    for tag in set(video_tags) - set(tags):
      cls.unlink(tag, video_id)

    cls.relink(tags, video_id)

  @classmethod
  def edit(cls, tag_id, **kwargs):
    tag = cls.get_by_id(tag_id)
    if 'name' in kwargs and not kwargs['name']:
      return 0, 'Name cannot be empty'

    with db.atomic():
      cls.update(**kwargs).where(cls.id == tag).execute()

      # Replace videos `tags` attr
      for video in VideoTag.videos(tag):
        video.tags = ','.join([kwargs['name'] if t == tag.name else t for t in filtertags(video.tags).split(',')])
        video.save()

    return 1, tag.id

  @classmethod
  def unlink(cls, tag, video_id):
    if isinstance(tag, str):
      tag = cls.get(cls.name == tag)
    if not VideoTag.select().where(VideoTag.tag == tag, VideoTag.video != video_id).exists():
      tag.delete_instance()

  @classmethod
  def relink(cls, tags, video_id):
    VideoTag.delete().where(VideoTag.video == video_id).execute()

    _tags = {tag.name: tag for tag in cls.select().where(cls.name << tags)}
    for tag in tags:
      VideoTag.create(tag = _tags[tag].id, video = video_id)


class VideoTag(Model):
  tag = ForeignKeyField(Tag, backref='tags', on_delete='CASCADE')
  video = ForeignKeyField(Video, on_delete='CASCADE')
  sort = IntegerField(default=0, index=True)
  created_at = DateTimeField(default=datetime.datetime.now)

  class Meta:
    database = db
    db_table = 'video_tags'
    indexes = (
      (('tag', 'video'), True),
    )

  @classmethod
  def tags(cls, video):
    return [vtag.tag for vtag in cls.select().join(Tag).where(cls.video == video)]

  @classmethod
  def videos(cls, tag):
    return [vtag.video for vtag in cls.select().join(Video).where(cls.tag == tag)]

  @classmethod
  def blend(cls, tag):
    return [{**model_to_dict(vtag.video), 'sort': vtag.sort, 'code': None}
      for vtag in cls.select().join(Tag).switch(cls).join(Video).order_by(cls.sort, cls.id).where(cls.tag == tag)]

  @classmethod
  def save_videos(cls, tag, videos):
    with db.atomic():
      for video in videos:
        video_id = video.pop('id')
        cls.update({**video}).where(cls.tag == tag, cls.video == video_id).execute()

    return 1, 'OK'

class Secret(Model):
  iv = CharField()
  key = TextField()
  created_at = DateTimeField(default=datetime.datetime.now)

  class Meta:
    database = db
    db_table = 'secrets'

  @classmethod
  def add(cls, iv, key):
    secret = cls.create(iv=iv, key=key)
    return 1, secret.id




db.create_tables([Tag, Video, Secret, VideoTag], safe=True)
