#!/usr/bin/env python

import glob
import random
import shutil
import tempfile

from os import subprocess
from zipfile import ZipFile

import math

from . import logger


def via_mangapy(mangapy_source, chapter, target_directory):
    successfully_downloaded = False
    temp_directory = tempfile.mkdtemp(prefix="cc_download_mangapy") + "/"

    try:
        command = ["manga-py",
                   "--rewrite-exists-archives",
                   "--skip-volumes", str(int(chapter) - 1),
                   "--max-volumes", "1",
                   "--name", "downloaded",
                   "-d", temp_directory,
                   # Random attempt(s) to make the DL not silently fail....
                   "--min-free-space", str(math.ceil(random.random() * 100)),
                   mangapy_source]
        subprocess.Popen(command, shell=True, close_fds=False,
                            stdin=subprocess.PIPE, stderr=subprocess.STDOUT,
                            stdout=subprocess.PIPE).communicate()
        downloaded_zips = glob.glob(temp_directory + "**/*.zip")

        if len(downloaded_zips) == 0:
            logger.info("Couldn't find downloaded zip folder"
                        "\n(download may have failed or you may already have the zip)")
        elif len(downloaded_zips) > 1:
            logger.info("Detected multiple new downloaded zip folders: " + str(downloaded_zips) +
                        "\n(can't determine which one to use, aborting)")
        else:
            with ZipFile(downloaded_zips[0], 'r') as zipObj:
                zipObj.extractall(target_directory)
            successfully_downloaded = True
    finally:
        shutil.rmtree(temp_directory, ignore_errors=True)

    return successfully_downloaded
