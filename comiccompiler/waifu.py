#!/usr/bin/env python

import requests
import glob


def waifu(key, file_pattern):
    file_save_names = []

    for filename in glob.glob(file_pattern):
        file_name_set = filename.rsplit('.')
        file_save_names.append(''.join((file_name_set[0], '-waifud.', file_name_set[-1])))

        try:
            url = post_image(key, filename)
            img_dl = requests.get(url, allow_redirects=True)
        except requests.HTTPError:
            print('Something wrong with the Internet, please try again later.')
        else:
            with open(file_save_names[-1], 'wb') as hand:
                hand.write(img_dl.content)

    return file_save_names


def post_image(key, filename):
    res = requests.post(
        "https://api.deepai.org/api/waifu2x",
        files={
            'image': open(filename, 'rb'),
        },
        headers={'api-key': key}
    )
    # print(res.json())
    return res.json()['output_url']
