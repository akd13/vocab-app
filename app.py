from flask import Flask, render_template, request, redirect, url_for
import nltk
nltk.download('wordnet')
from model.word import create_tables, find_word, get_definition, get_synonyms, get_images, insert_word, \
    insert_definition, insert_synonyms, insert_images
from vocab.utils import pick_random_word
from vocab.word_details import get_definition_synonyms
from vocab.word_images import download_images

create_tables()

app = Flask(__name__)

home_dir = './static/images/'


@app.route('/',methods=['POST', 'GET'])
def pick_word():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        return redirect(url_for('define_word', word=pick_random_word()))


@app.route('/define/<string:word>/', methods=['POST', 'GET'])
def define_word(word: str):
    # check if word in table
    result = find_word(word.lower())
    if result is None:
        definition, synonyms = get_definition_synonyms(word)
        is_empty = len(definition) == 0 and len(synonyms) == 0
        images = download_images(word, home_dir) if not is_empty else []
        # insert into table
        word_id = insert_word(word.lower())
        insert_definition(word_id, definition)
        insert_synonyms(word_id, synonyms)
        insert_images(word_id, images)
    else:
        definition = get_definition(result.id)
        synonyms = get_synonyms(result.id)
        images = get_images(result.id)
    if request.method == 'GET':
        return render_template('word.html', word=word, definition=definition, synonyms=synonyms, images=images)
    else:
        form_keys = request.form.keys()
        if 'next' in form_keys:
            return redirect(url_for('define_word', word=pick_random_word()))
        else:
            return redirect(url_for('define_word', word=request.form['Word']))


if __name__ == '__main__':
    app.run()
