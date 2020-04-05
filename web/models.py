import datetime
from peewee import *
from utils import md5, validjson, filtertags
db = SqliteDatabase('data.db', pragmas={'foreign_keys': 1})

class Video(Model):
  slug = CharField(unique=True)
  tags = CharField()
  code = TextField()
  title = CharField()
  params = TextField()
  created_at = DateTimeField(default=datetime.datetime.now)
  updated_at = DateTimeField(null=True)

  class Meta:
    database = db
    db_table = 'videos'

  @classmethod
  def remove(cls, id):
    with db.atomic():
      tags = [vtag.tag for vtag in VideoTag.select().join(Tag).where(VideoTag.video == id)]
      for tag in tags: Tag.unlink(tag, id)

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
    kwargs['tags'] = filtertags(kwargs['tags'])

    with db.atomic():
      if kwargs['id']:
        video_id = kwargs['id']
        cls.update(**kwargs).where(cls.id == kwargs['id']).execute()
      else:
        kwargs.pop('id')
        video_id = cls.create(**kwargs).id
      Tag.add(kwargs['tags'], video_id)

    return 1, video_id


class Tag(Model):
  name = CharField(unique=True)
  created_at = DateTimeField(default=datetime.datetime.now)

  class Meta:
    database = db
    db_table = 'tags'

  @classmethod
  def add(cls, tags, video_id):
    tags       = tags.split(',')
    all_tags   = [tag.name for tag in Tag.select().where(Tag.name << tags)]
    video_tags = [vtag.tag.name for vtag in VideoTag.select().where(VideoTag.video == video_id)]

    for tag in set(tags) - set(all_tags):
      cls.create(name = tag)
    for tag in set(video_tags) - set(tags):
      cls.unlink(tag, video_id)

    cls.relink(tags, video_id)

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
  created_at = DateTimeField(default=datetime.datetime.now)

  class Meta:
    database = db
    db_table = 'video_tags'
    indexes = (
      (('tag', 'video'), True),
    )


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
