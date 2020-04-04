import datetime
from peewee import *

db = SqliteDatabase('data.db')

class Tag(Model):
  name = CharField()
  created_at = DateTimeField(default=datetime.datetime.now)

class Video(Model):
  slug = CharField(unique=True)
  code = TextField()
  title = CharField()
  params = TextField()
  created_at = DateTimeField(default=datetime.datetime.now)
  updated_at = DateTimeField(null=True)

  class Meta:
    database = db


class Secret(Model):
  iv = CharField()
  key = TextField()
  created_at = DateTimeField(default=datetime.datetime.now)

  class Meta:
    database = db


db.create_tables([Video, Secret], safe=True)
