from peewee import *

db = SqliteDatabase('sqlite.db')

class Word(Model):
    word = CharField()
    definition = DateField()
    synonym

    class Meta:
        database = db