from flask import Flask, render_template, request, redirect, url_for
import nltk

nltk.download("wordnet")

from model.word import WordRepository
from vocab.utils import WordPicker
from vocab.word_details import WordDetailsService
from vocab.word_images import ImageDownloader

repo = WordRepository()
repo.create_tables()

picker = WordPicker()
details_service = WordDetailsService()
image_downloader = ImageDownloader()

app = Flask(__name__)

home_dir = './static/images/'


@app.route('/',methods=['POST', 'GET'])
def pick_word():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        return redirect(url_for('define_word', word=picker.pick()))


@app.route('/define/<string:word>/', methods=['POST', 'GET'])
def define_word(word: str):
    # check if word in table
    result = repo.find_word(word.lower())
    if result is None:
        definition, synonyms = details_service.get_details(word)
        is_empty = len(definition) == 0 and len(synonyms) == 0
        images = image_downloader.download(word, home_dir) if not is_empty else []
        # insert into table
        word_id = repo.insert_word(word.lower())
        repo.insert_definition(word_id, definition)
        repo.insert_synonyms(word_id, synonyms)
        repo.insert_images(word_id, images)
    else:
        definition = repo.get_definition(result.id)
        synonyms = repo.get_synonyms(result.id)
        images = repo.get_images(result.id)
    if request.method == 'GET':
        return render_template('word.html', word=word, definition=definition, synonyms=synonyms, images=images)
    else:
        form_keys = request.form.keys()
        if 'next' in form_keys:
            return redirect(url_for('define_word', word=picker.pick()))
        else:
            return redirect(url_for('define_word', word=request.form['Word']))


if __name__ == '__main__':
    app.run()
