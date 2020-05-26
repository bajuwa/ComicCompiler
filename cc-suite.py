#!/usr/bin/env python

import argparse
import configparser
import glob
import os
import random
import shutil
import subprocess
import tempfile

import math
import comicom

from comiccompiler import localfiles, waifu, imgmag, logger
from zipfile import ZipFile
from PIL import Image


def main():
    args = extract_args()
    series_config = load_config(args.series)

    logger.info("Processing series [{series}] chapter(s) {chapter}".format(series=args.series, chapter=args.chapters))

    folders = Directories(series_config.working_directory, series_config.folder_name)

    for chapter in args.chapters:
        logger.info("")
        logger.info("Processing series [{series}] chapter {chapter}".format(series=args.series, chapter=chapter))
        folders.chapter_folder_name = "ch" + str(chapter).zfill(3)
        folders.input_chapter = folders.input + folders.chapter_folder_name + "/"
        folders.compiled_chapter = folders.compiled + folders.chapter_folder_name + "/"

        if not _ensure_input_images(series_config, folders, chapter):
            continue

        _remove_ads(series_config, folders)
        _waifu_input(series_config, folders)
        _compile_input(series_config, folders, args.series)


def extract_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--config', nargs=0, action=OpenConfig, help='Opens the config file for editing')
    parser.add_argument('series', help='The key used for the series (should match the [series] line in the config)')
    parser.add_argument('chapters', nargs='+', action=IntOrRange, help='The chapters the should be processed')
    return parser.parse_args()


def _ensure_input_images(series_config, directories, chapter):
    if len(glob.glob(directories.input_chapter + "*.*")) > 0:
        logger.info("Found existing items in input folder, skipping download: "
              + str(glob.glob(directories.input_chapter)))
        return True

    elif len(series_config.mangapy_source) > 0:
        logger.info("Using mangapy to download from: " + series_config.mangapy_source)

        previous_zips = glob.glob(directories.downloaded + "*.zip")
        command = ["manga-py",
                   "--rewrite-exists-archives",
                   "--skip-volumes", str(int(chapter) - 1),
                   "--max-volumes", "1",
                   "--name", "downloaded",
                   "-d", directories.series,
                   # Random attempt(s) to make the DL not silently fail....
                   "--min-free-space", str(math.ceil(random.random() * 100)),
                   series_config.mangapy_source]
        subprocess.Popen(command, shell=True, close_fds=False,
                         stdin=subprocess.PIPE, stderr=subprocess.STDOUT,
                         stdout=subprocess.PIPE).communicate()
        current_zips = glob.glob(directories.downloaded + "*.zip")
        downloaded_zips = list(set(current_zips) - set(previous_zips))

        if len(downloaded_zips) == 0:
            logger.info("Couldn't find downloaded zip folder to: " + directories.downloaded +
                  "\n(download may have failed or you may already have the zip)")
            return False
        elif len(downloaded_zips) > 1:
            logger.info("Detected multiple new downloaded zip folders: " + str(downloaded_zips) +
                  "\n(can't determine which one to use, aborting)")
            return False

        with ZipFile(downloaded_zips[0], 'r') as zipObj:
            zipObj.extractall(directories.input_chapter)
    else:
        logger.info("Unable to find existing input and no download url given, moving items from: "
              + series_config.local_input)
        local_files = glob.glob(series_config.local_input)
        if len(local_files) == 0:
            logger.info("No files found in local directory")
            return False
        else:
            if not os.path.exists(directories.input_chapter):
                os.mkdir(directories.input_chapter)
            for file in local_files:
                shutil.move(file, directories.input_chapter)

    return True


def _remove_ads(series_config, folders):
    if len(series_config.ads_folder) > 0:
        logger.info("Checking folder for ads to remove: " + series_config.ads_folder)
        ads = glob.glob(series_config.ads_folder + "*.*")
        input_files = glob.glob(folders.input_chapter + "*.jp*g")
        if len(ads) == 0 or len(input_files) == 0:
            return

        logger.info("Checking for any input images that roughly match these ad files: " + str(ads))
        i = len(input_files) - 1
        while any(imgmag.almost_matches(input_files[i], ad) for ad in ads):
            logger.info("Removing ad: " + input_files[i])
            os.remove(input_files[i])
            i -= 1

        i = 0
        while any(imgmag.almost_matches(input_files[i], ad) for ad in ads):
            logger.info("Removing ad: " + input_files[i])
            os.remove(input_files[i])
            i += 1


def _waifu_input(series_config, folders):
    if len(series_config.waifu_key) > 0:
        logger.info("Detected waifu key")
        if len(glob.glob(folders.input_chapter + "*waifud.*")) == 0:
            input_files = glob.glob(folders.input_chapter + "*.*")
            temp_directory = tempfile.mkdtemp(prefix="prewaifu") + "/"
            logger.info("Processing with waifu using temp directory: " + temp_directory)
            for input_file in input_files:
                split_to_temp(input_file, temp_directory)
            results = waifu.waifu(series_config.waifu_key, temp_directory + "*.*", folders.input_chapter)
            shutil.rmtree(temp_directory, ignore_errors=True)
            logger.info("Waifu'd " + str(len(results)) + " files")
        if len(series_config.arguments) > 0:
            series_config.arguments += " "
        series_config.arguments += "-f " + folders.input_chapter + "*-waifud.jp*g"


def split_to_temp(filepath, temp_directory):
    image = Image.open(filepath)
    # Create temp folder and copy files over (if <=800px high)
    if image.height <= 800:
        shutil.copy(filepath, temp_directory)
    else:
        # If >800px then waifu will return a file that isn't 2x width
        # (which will cause issues for compilation)
        print("Image was too tall to send to waifu (>800px), splitting before waifu: " + filepath)
        path, filename = os.path.split(filepath)
        filename_noext, extension = filename.split('.')
        imgmag.split(filepath, 800, temp_directory + filename_noext, extension)
    image.close()


def _compile_input(series_config, folders, series):
    full_arguments = "-f {input_chapter_folder}*[!waifud].* " \
                     "-od {compiled_chapter_folder} " \
                     "--clean".format(input_chapter_folder=folders.input_chapter,
                                      compiled_chapter_folder=folders.compiled_chapter,
                                      chapter_folder_name=folders.chapter_folder_name,
                                      series=series)
    if len(series_config.arguments) > 0:
        full_arguments += " " + series_config.arguments

    logger.info("Running comicom with final arguments: " + full_arguments)
    comicom.run(full_arguments)


def load_config(series):
    config_file = localfiles.get_cc_suite_config_file()
    logger.info("Using configs: " + config_file)
    config = configparser.ConfigParser()
    config.read(config_file)

    if config["default"] is None:
        logger.info("Unable to find required [default] section within the config file. \n"
              "It's recommended to delete your current config file and try again (a new one will be generated for you)")
        exit()

    blended_config = SeriesConfig(dict(config.items("default")))

    if series not in config.sections():
        logger.info("Could not find configuration for series key, proceeding with default config: {series}\n"
                    "Use 'cc-suite.py --config' to open the config file on your system and add a section for [{series}]"
                    .format(series=series))
        blended_config.folder_name = series
        return blended_config

    blended_config.load(dict(config.items(series)))

    if len(blended_config.folder_name) == 0:
        blended_config.folder_name = series

    if len(blended_config.working_directory) == 0:
        logger.info("Could not find configuration for: {key}\n"
              "Use 'cc-suite.py --config' to open the config file on your system and add a section for [{key}]"
              .format(key="working_directory"))
        exit()

    return blended_config


def open_file(filename):
    try:
        os.startfile(filename)
    except AttributeError:
        subprocess.call(['open', filename])


class OpenConfig(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):
        config_file = localfiles.get_cc_suite_config_file()
        logger.info("Opening config file: " + config_file)
        open_file(config_file)
        parser.exit()


class IntOrRange(argparse.Action):
    def __call__(self, parser, args, values, option_string=None):
        chapters = []
        try:
            for value in values:
                split = value.split('-')
                if len(split) == 1:
                    chapters.append(str(int(split[0])))
                elif len(split) == 2 and int(split[0]) < int(split[1]):
                    chapters += map(lambda v: str(v), range(int(split[0]), int(split[1]) + 1))
                else:
                    raise argparse.ArgumentTypeError('Invalid number of integers in the chapter range')
        except:
            raise argparse.ArgumentTypeError('Could not interpret input chapter numbers/ranges')

        setattr(args, self.dest, chapters)


class SeriesConfig:
    working_directory = None
    folder_name = None
    mangapy_source = None
    local_input = None
    ads_folder = None
    waifu_key = None
    arguments = ""

    def __init__(self, config_dict):
        self.load(config_dict)

    def load(self, source_dict):
        if "working_directory" in source_dict:
            self.working_directory = source_dict["working_directory"]
        if "folder_name" in source_dict:
            self.folder_name = source_dict["folder_name"]
        if "mangapy_source" in source_dict:
            self.mangapy_source = source_dict["mangapy_source"]
        if "local_input" in source_dict:
            self.local_input = source_dict["local_input"]
        if "ads_folder" in source_dict:
            self.ads_folder = source_dict["ads_folder"]
        if "waifu_key" in source_dict:
            self.waifu_key = source_dict["waifu_key"]
        if "arguments" in source_dict:
            if self.arguments is not None and len(self.arguments) > 0:
                self.arguments += " "
            self.arguments += source_dict["arguments"]


class Directories:

    def __init__(self, working_directory, folder_name):
        self.top = working_directory
        self.series = self.top + folder_name + "/"
        self.downloaded = self.series + "downloaded/"
        self.input = self.series + "input/"
        self.compiled = self.series + "compiled/"

        for attribute, value in self.__dict__.items():
            localfiles.ensure_directory(value)

        self.chapter_folder_name = None
        self.input_chapter = None
        self.compiled_chapter = None


if __name__ == '__main__':
    main()
