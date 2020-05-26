#!/usr/bin/env python
import os

import requests
import glob

from comiccompiler import logger


def waifu(key, file_pattern, target_directory):
    waifud_filepaths = []

    for filepath in glob.glob(file_pattern):
        path, filename = os.path.split(filepath)
        filename_noext, extension = filename.split('.')
        waifud_filepaths.append(''.join((target_directory, filename_noext, '-waifud.', extension)))

        try:
            url = post_image(key, filepath)
            img_dl = requests.get(url, allow_redirects=True)
        except requests.HTTPError:
            logger.error('Something wrong with the Internet, please try again later.')
        else:
            with open(waifud_filepaths[-1], 'wb') as hand:
                hand.write(img_dl.content)

    return waifud_filepaths


def post_image(key, filename):
    res = requests.post(
        "https://api.deepai.org/api/waifu2x",
        files={
            'image': open(filename, 'rb'),
        },
        headers={'api-key': key}
    )
    # logger.info(res.json())
    return res.json()['output_url']
