import os

from peewee import SqliteDatabase, Model, CharField, ForeignKeyField
from playhouse.db_url import connect

db = SqliteDatabase('sqlite.db')


if os.getenv('ENVIRONMENT', '') == 'local':
    db = SqliteDatabase('sqlite.db')
else:
    db = connect(os.getenv('DATABASE_URL', ''))


class Word(Model):
    word = CharField()

    class Meta:
        database = db


class Definition(Model):
    word = ForeignKeyField(Word)
    definition = CharField()

    class Meta:
        database = db


class Synonym(Model):
    word = ForeignKeyField(Word)
    synonym = CharField()

    class Meta:
        database = db


class Image(Model):
    word = ForeignKeyField(Word)
    image = CharField()

    class Meta:
        database = db


def create_tables():
    with db:
        db.create_tables([Word, Definition, Synonym, Image])


def find_word(word: str):
    result = Word.select().where(Word.word == word)
    return result.get() if result else None


def get_definition(word_id: int):
    result = Definition.select(Definition.definition).where(Definition.word_id == word_id)
    definition = result.get().definition
    return definition


def get_synonyms(word_id: int):
    result = Synonym.select(Synonym.synonym).where(Synonym.word_id == word_id)
    synonyms = [r.synonym for r in result]
    return synonyms


def get_images(word_id: int):
    result = Image.select(Image.image).where(Image.word_id == word_id)
    images = [r.image for r in result]
    return images


def insert_word(word: str):
    return Word.insert(word=word).execute()


def insert_definition(word_id: int, definition: str):
    definition_list = {'word_id': word_id, 'definition': definition}
    Definition.insert(definition_list).execute()


def insert_synonyms(word_id: int, synonyms: list):
    synonym_list = [{'word_id': word_id, 'synonym': synonym} for synonym in synonyms]
    Synonym.insert_many(synonym_list).execute()


def insert_images(word_id: int, images: list):
    image_list = [{'word_id': word_id, 'image': image} for image in images]
    Image.insert_many(image_list).execute()
