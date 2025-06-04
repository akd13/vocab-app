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


class WordRepository:
    """Utility class wrapping common database operations."""

    def __init__(self, database=db) -> None:
        self.db = database

    def create_tables(self) -> None:
        with self.db:
            self.db.create_tables([Word, Definition, Synonym, Image])

    def find_word(self, word: str):
        result = Word.select().where(Word.word == word)
        return result.get() if result else None

    def get_definition(self, word_id: int) -> str:
        result = Definition.select(Definition.definition).where(Definition.word_id == word_id)
        row = result.get() if result else None
        return row.definition if row else ""

    def get_synonyms(self, word_id: int):
        result = Synonym.select(Synonym.synonym).where(Synonym.word_id == word_id)
        return [r.synonym for r in result]

    def get_images(self, word_id: int):
        result = Image.select(Image.image).where(Image.word_id == word_id)
        return [r.image for r in result]

    def insert_word(self, word: str):
        return Word.insert(word=word).execute()

    def insert_definition(self, word_id: int, definition: str):
        Definition.insert({"word_id": word_id, "definition": definition}).execute()

    def insert_synonyms(self, word_id: int, synonyms: list):
        synonym_list = [{"word_id": word_id, "synonym": syn} for syn in synonyms]
        Synonym.insert_many(synonym_list).execute()

    def insert_images(self, word_id: int, images: list):
        image_list = [{"word_id": word_id, "image": img} for img in images]
        Image.insert_many(image_list).execute()


# Backwards compatible helpers
_repo = WordRepository()


def create_tables():
    _repo.create_tables()


def find_word(word: str):
    return _repo.find_word(word)


def get_definition(word_id: int):
    return _repo.get_definition(word_id)


def get_synonyms(word_id: int):
    return _repo.get_synonyms(word_id)


def get_images(word_id: int):
    return _repo.get_images(word_id)


def insert_word(word: str):
    return _repo.insert_word(word)


def insert_definition(word_id: int, definition: str):
    _repo.insert_definition(word_id, definition)


def insert_synonyms(word_id: int, synonyms: list):
    _repo.insert_synonyms(word_id, synonyms)


def insert_images(word_id: int, images: list):
    _repo.insert_images(word_id, images)
