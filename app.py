from flask import Flask, render_template, request, redirect, url_for, jsonify
import nltk
from functools import lru_cache
import asyncio
from concurrent.futures import ThreadPoolExecutor
import os

nltk.download("wordnet")

from model.word import WordRepository
from vocab.utils import WordPicker
from vocab.word_details import WordDetailsService
from vocab.word_images import ImageDownloader

# Initialize components
repo = WordRepository()
repo.create_tables()

picker = WordPicker()
details_service = WordDetailsService()
image_downloader = ImageDownloader()

app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=4)

home_dir = './static/images/'

@lru_cache(maxsize=1000)
def get_word_details(word):
    return details_service.get_details(word)

async def process_word(word):
    # Check if word exists in database
    result = repo.find_word(word.lower())
    if result is None:
        # Get word details and images concurrently
        definition, synonyms = get_word_details(word)
        is_empty = len(definition) == 0 and len(synonyms) == 0
        
        # Download images in background if word has details
        images = []
        if not is_empty:
            images = await image_downloader.download_async(word, home_dir)
        
        # Insert into database
        word_id = repo.insert_word(word.lower())
        repo.insert_definition(word_id, definition)
        repo.insert_synonyms(word_id, synonyms)
        repo.insert_images(word_id, images)
    else:
        definition = repo.get_definition(result['id'])
        synonyms = repo.get_synonyms(result['id'])
        images = repo.get_images(result['id'])
    
    return definition, synonyms, images

@app.route('/', methods=['POST', 'GET'])
def pick_word():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        return redirect(url_for('define_word', word=picker.pick()))

@app.route('/define/<string:word>/', methods=['POST', 'GET'])
def define_word(word):
    # Check if word exists in database
    result = repo.find_word(word.lower())
    if result is None:
        # Get word details and images concurrently
        definition, synonyms = get_word_details(word)
        is_empty = len(definition) == 0 and len(synonyms) == 0
        
        # Insert into database
        word_id = repo.insert_word(word.lower())
        repo.insert_definition(word_id, definition)
        repo.insert_synonyms(word_id, synonyms)
    else:
        definition = repo.get_definition(result['id'])
        synonyms = repo.get_synonyms(result['id'])
    
    if request.method == 'GET':
        return render_template('word.html', word=word, definition=definition, synonyms=synonyms, images=[])
    else:
        form_keys = request.form.keys()
        if 'next' in form_keys:
            return redirect(url_for('define_word', word=picker.pick()))
        else:
            return redirect(url_for('define_word', word=request.form['Word']))

@app.route('/images/<string:word>/', methods=['GET'])
async def get_images(word):
    print(f"\nProcessing images for word: {word}")  # Debug
    # Check if word exists in database
    result = repo.find_word(word.lower())
    images = []
    
    if result is None:
        print(f"Word {word} not found in database, will create new entry")  # Debug
        # Create new word entry
        word_id = repo.insert_word(word.lower())
        result = {'id': word_id}
    else:
        images = repo.get_images(result['id'])
        print(f"Images from database: {images}")  # Debug
    
    if not images:
        # Ensure the images directory exists
        os.makedirs(home_dir, exist_ok=True)
        
        # Check if images exist in static directory first
        static_images = []
        try:
            for filename in os.listdir(home_dir):
                if filename.lower().startswith(word.lower()):
                    static_images.append(filename)
            print(f"Found static images: {static_images}")  # Debug
        except FileNotFoundError:
            print(f"Images directory not found: {home_dir}")  # Debug
            os.makedirs(home_dir, exist_ok=True)
            static_images = []
        
        if static_images:
            # If we found images in static directory, use those
            word_id = result['id']
            # Insert the new images without deleting existing ones
            repo.insert_images(word_id, static_images)
            images = static_images
        else:
            # If no static images found, trigger background image download using DuckDuckGo
            try:
                # Create a new image downloader instance for this request
                downloader = ImageDownloader()
                try:
                    # Use DuckDuckGo API to get images
                    new_images = await downloader.download_async(word, home_dir)
                    print(f"Downloaded new images: {new_images}")  # Debug
                    if new_images:  # Only insert if we got images
                        word_id = result['id']
                        repo.insert_images(word_id, new_images)
                        images = new_images
                finally:
                    # Always close the downloader's session
                    await downloader.close()
            except Exception as e:
                print(f"Error downloading images for {word}: {e}")
                images = []
    
    # Convert relative paths to URLs
    image_urls = []
    for img in images:
        print(f"Processing image path: {img}")  # Debug
        # Clean up the path - remove any prefixes and ensure it's just the filename
        if img.startswith('./'):
            img = img[2:]  # Remove './' prefix
        if img.startswith('static/'):
            img = img[7:]  # Remove 'static/' prefix
        if img.startswith('images/'):
            img = img[7:]  # Remove 'images/' prefix if present
        
        # Ensure the path is relative to static/images
        if not img.startswith('images/'):
            img = os.path.join('images', img)
        
        final_url = url_for('static', filename=img)
        print(f"Generated URL: {final_url}")  # Debug
        image_urls.append(final_url)
    
    print(f"Final image URLs: {image_urls}")  # Debug
    return jsonify({"images": image_urls})

if __name__ == '__main__':
    app.run(threaded=True)
