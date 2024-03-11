import datetime
import os
from common_stuff import db_path
import peewee as pw


db_sqlite = pw.SqliteDatabase(db_path, pragmas={
    'journal_mode': 'wal',
    'cache_size': -1024 * 64})
db_sqlite.pragma('foreign_keys', 1, permanent=True)


class BaseModel(pw.Model):
    class Meta:
        database = db_sqlite


class User(BaseModel):
    chat_id = pw.BigIntegerField(unique=True)
    language = pw.CharField(max_length=50)
    action = pw.CharField(max_length=1)
    locale = pw.CharField(max_length=50)
    currency = pw.CharField(max_length=5)
    order = pw.CharField(max_length=255)
    destination_id = pw.CharField(max_length=255)
    destination_name = pw.CharField(max_length=255)
    min_price = pw.CharField(max_length=255)
    max_price = pw.CharField(max_length=255)
    distance = pw.CharField(max_length=255)
    quantity = pw.CharField(max_length=255)
    pictures_count = pw.IntegerField(default=0)
    date_from = pw.CharField(max_length=255)
    date_to = pw.CharField(max_length=255)


class History(BaseModel):
    user = pw.ForeignKeyField(User)
    date_time = pw.DateTimeField(default=datetime.datetime.utcnow())
    event = pw.CharField(max_length=255)
    search_result = pw.TextField()


def init_database():
    if not os.path.isfile(db_path):
        db_sqlite.create_tables([User, History])


if __name__ == '__main__':
    db_sqlite.create_tables([User, History])
