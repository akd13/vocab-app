import json
import re
import shutil
import requests
import os
from duckduckgo_search import DDGS

url = 'https://duckduckgo.com/'


def search(keyword):
    results = DDGS().images(
        keywords=keyword
    )

    return results[:3]


def download_images(keyword, home_dir):
    images = search(keyword)
    image_paths = []
    for i, image in enumerate(images):
        try:
            r = requests.get(image['image'], stream=True, timeout=8, verify=True)
            if not os.path.exists(home_dir):
                os.makedirs(home_dir)
            if r.status_code == 200:
                extension = '.' + image['image'].split('.')[-1]
                if len(extension) <= 5:
                    filepath = home_dir + keyword + str(i) + extension
                    r.raw.decode_content = True
                    f = open(filepath, 'wb')
                    f.write(r.content)
                    f.close()
                    image_paths.append(filepath[1:])
        except Exception as e:
            print(e)
    return image_paths
