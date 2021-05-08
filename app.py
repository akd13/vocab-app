from flask import Flask, render_template
from word_details import get_definition_synonyms
from image_result import download_images
import os

app = Flask(__name__)

home_dir = './static/images/'


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/<string:word>')
def define_word(word):
    # check if word in table
    definitions, synonyms = get_definition_synonyms(word)
    images = download_images(word, home_dir)
    return render_template('word.html', word=word, definitions=definitions, synonyms=synonyms, images=images)


if __name__ == '__main__':
    app.run()
