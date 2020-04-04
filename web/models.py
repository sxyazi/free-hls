import datetime
from peewee import *
from utils import md5, validjson
db = SqliteDatabase('data.db')

class Video(Model):
  slug = CharField(unique=True)
  code = TextField()
  title = CharField()
  params = TextField()
  created_at = DateTimeField(default=datetime.datetime.now)
  updated_at = DateTimeField(null=True)

  class Meta:
    database = db
    db_table = 'videos'

  @classmethod
  def save(cls, code, title, params):
    if not code:
      return 0, 'Code cannot be empty'
    elif len(code) > 500*1024:
      return 0, 'Code size cannot exceed 500K'
    elif not validjson(params):
      return 0, 'Invalid params'

    slug = md5(code)
    return 1, cls.replace(slug = slug, code = code, title = title, params = params).execute()

  @classmethod
  def remove(cls, id):
    with db.atomic():
      video = cls.get_by_id(id)
      cls.delete().where(cls.id == id).execute()
      Tag.unlink(video.tag, video.video)

    return 1


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


class Tag(Model):
  name = CharField(unique=True)
  created_at = DateTimeField(default=datetime.datetime.now)

  class Meta:
    database = db
    db_table = 'tags'

  @classmethod
  def add(cls, name):
    cls.create(name = name)

  @classmethod
  def remove(cls, name):
    pass

  @classmethod
  def unlink(cls, tag_id, video_id):
    if not VideoTag.select().where(VideoTag.tag == tag_id, VideoTag.video != video_id).exists():
      cls.delete().where(cls.id == tag_id).delete_instance()


class VideoTag(Model):
  tag = ForeignKeyField(Tag, backref='tags', on_delete='CASCADE')
  video = ForeignKeyField(Video, backref='tags', on_delete='CASCADE')
  created_at = DateTimeField(default=datetime.datetime.now)

  class Meta:
    database = db
    db_table = 'video_tags'


db.create_tables([Tag, Video, Secret, VideoTag], safe=True)
