from flask import Flask, render_template

from word_details import get_definition_synonyms
from word_images import download_images
from model.word import create_tables, find_word, get_definitions, get_synonyms, get_images, insert_word, \
    insert_definitions, insert_synonyms, insert_images
import sys, os
create_tables()

app = Flask(__name__)

home_dir = './static/images/'
os.mkdir(home_dir)

@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/<string:word>')
def define_word(word):
    # check if word in table
    result = find_word(word)
    if result is None:
        definitions, synonyms = get_definition_synonyms(word)
        images = download_images(word, home_dir)
        print(images, 'IMAGES FROM MAIN AKANKSHITA')
        sys.stdout.flush()
        # insert into table
        word_id = insert_word(word)
        insert_definitions(word_id, definitions)
        insert_synonyms(word_id, synonyms)
        insert_images(word_id, images)
    else:
        definitions = get_definitions(result.id)
        synonyms = get_synonyms(result.id)
        images = get_images(result.id)
    return render_template('word.html', word=word, definitions=definitions, synonyms=synonyms, images=images)


if __name__ == '__main__':
    app.debug = True
    app.run()
