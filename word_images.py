import json
import re
import shutil
import requests
import os

url = 'https://duckduckgo.com/'


def search(keywords):
    params = get_auth_token(keywords)

    request_url = url + "i.js"
    response = requests.get(request_url, params=params)
    image_url = json.loads(response.text)
    return image_url["results"][:3]


def get_auth_token(keywords):
    response = requests.post(url, data={'q': keywords})
    auth_token = re.search(r'vqd=([\d-]+)', response.text, re.M | re.I)
    params = (
        ('q', keywords),
        ('vqd', auth_token.group(1))
    )
    return params


def download_images(keyword, home_dir):
    images = search(keyword)
    image_paths = []
    for i, image in enumerate(images):
        try:
            r = requests.get(image['image'], stream=True, timeout=8, verify=True)
            print(r.status_code, 'STATUS CODE')
            if r.status_code == 200:
                extension = '.' + image['image'].split('.')[-1]
                if len(extension) <= 5:
                    print('INSIDE LOOP')
                    filepath = home_dir + keyword + str(i) + extension
                    r.raw.decode_content = True
                    print("DECODING")
                    with open(filepath, 'wb') as f:
                        print("OPENED FILE")
                        f.write(r.content)
                        f.close()
                        print("COPIED FILE")
                    image_paths.append(filepath)
        except Exception as e:
            print(e, 'EXCEPTION HERE')
    print(image_paths, os.getcwd(), 'AKANKSHITA')
    return image_paths
