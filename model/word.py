from peewee import SqliteDatabase, Model, CharField
import sqlite3
import os
from functools import lru_cache
from playhouse.db_url import connect

db = SqliteDatabase('sqlite.db')

if os.getenv('ENVIRONMENT', '') == 'local':
    db = SqliteDatabase('sqlite.db')
else:
    db = connect(os.getenv('DATABASE_URL', ''))


class WordData(Model):
    word = CharField()
    definition = CharField(null=True)
    synonym = CharField(null=True)
    image = CharField(null=True)

    class Meta:
        database = db


class WordRepository:
    """Utility class wrapping common database operations."""

    def __init__(self):
        self.conn = sqlite3.connect('sqlite.db', check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # Add indexes for faster lookups
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT UNIQUE NOT NULL
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_word ON words(word)')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS definitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_id INTEGER NOT NULL,
                definition TEXT NOT NULL,
                FOREIGN KEY (word_id) REFERENCES words(id)
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_word_id ON definitions(word_id)')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS synonyms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_id INTEGER NOT NULL,
                synonym TEXT NOT NULL,
                FOREIGN KEY (word_id) REFERENCES words(id)
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_synonym_word_id ON synonyms(word_id)')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word_id INTEGER NOT NULL,
                image_path TEXT NOT NULL,
                FOREIGN KEY (word_id) REFERENCES words(id)
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_image_word_id ON images(word_id)')
        
        self.conn.commit()

    @lru_cache(maxsize=1000)
    def find_word(self, word):
        cursor = self.conn.cursor()
        return cursor.execute('SELECT * FROM words WHERE word = ?', (word,)).fetchone()

    def insert_word(self, word):
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO words (word) VALUES (?)', (word,))
        self.conn.commit()
        # Clear cached lookup so new word is returned on subsequent calls
        self.find_word.cache_clear()
        # Fetch the word ID (either newly inserted or existing)
        cursor.execute('SELECT id FROM words WHERE word = ?', (word,))
        result = cursor.fetchone()
        return result['id'] if result else None

    def insert_definition(self, word_id, definition):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO definitions (word_id, definition) VALUES (?, ?)',
                      (word_id, definition))
        self.conn.commit()
        # Invalidate cached definitions
        self.get_definition.cache_clear()

    def insert_synonyms(self, word_id, synonyms):
        cursor = self.conn.cursor()
        for synonym in synonyms:
            cursor.execute('INSERT INTO synonyms (word_id, synonym) VALUES (?, ?)',
                           (word_id, synonym))
        self.conn.commit()
        # Invalidate cached synonyms
        self.get_synonyms.cache_clear()

    def insert_images(self, word_id, images):
        cursor = self.conn.cursor()
        for image in images:
            cursor.execute('INSERT INTO images (word_id, image_path) VALUES (?, ?)',
                           (word_id, image))
        self.conn.commit()
        # Invalidate cached images so duplicates aren't downloaded
        self.get_images.cache_clear()

    @lru_cache(maxsize=1000)
    def get_definition(self, word_id):
        cursor = self.conn.cursor()
        result = cursor.execute('SELECT definition FROM definitions WHERE word_id = ?',
                              (word_id,)).fetchone()
        return result['definition'] if result else ""

    @lru_cache(maxsize=1000)
    def get_synonyms(self, word_id):
        cursor = self.conn.cursor()
        results = cursor.execute('SELECT synonym FROM synonyms WHERE word_id = ?',
                               (word_id,)).fetchall()
        return [row['synonym'] for row in results]

    @lru_cache(maxsize=1000)
    def get_images(self, word_id):
        cursor = self.conn.cursor()
        results = cursor.execute('SELECT image_path FROM images WHERE word_id = ?',
                                (word_id,)).fetchall()
        # Limit to three images to prevent multiple sets from showing
        return [row['image_path'] for row in results][:3]