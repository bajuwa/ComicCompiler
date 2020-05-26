#!/usr/bin/env python
import asyncio
import os
from concurrent.futures.thread import ThreadPoolExecutor

import requests
import glob

from comiccompiler import logger


def waifu(key, file_pattern, target_directory):
    target_filepaths = []

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(_waifu_asynchronously(target_filepaths, key, file_pattern, target_directory))
    loop.run_until_complete(future)

    return target_filepaths


async def _waifu_asynchronously(target_filepaths, key, file_pattern, target_directory):
    source_filepaths = glob.glob(file_pattern)

    for filepath in source_filepaths:
        path, filename = os.path.split(filepath)
        filename_noext, extension = filename.split('.')
        target_filepaths.append(''.join((target_directory, filename_noext, '-waifud.', extension)))

    with ThreadPoolExecutor(max_workers=10) as executor:
        with requests.Session() as session:
            loop = asyncio.get_event_loop()

            tasks = [
                loop.run_in_executor(
                    executor,
                    _waifu_single_file,
                    *(session, key, source_filepaths[i], target_filepaths[i])
                )
                for i in range(len(source_filepaths))
            ]

            for response in await asyncio.gather(*tasks):
                pass

    return target_filepaths


def _waifu_single_file(session, key, source, target):
    try:
        url = post_image(key, source)
        img_dl = session.get(url, allow_redirects=True)
    except requests.HTTPError:
        logger.error('Something wrong with the Internet, please try again later.')
    else:
        with open(target, 'wb') as hand:
            hand.write(img_dl.content)


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
