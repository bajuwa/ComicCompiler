import glob
import os


comicom_profiles_directory = "comicom_profiles"
cc_suite_config_directory = "cc_suite_config"
cc_suite_config_file = "cc-suite-config.ini"


def load_profile(profile_name):
    if profile_name is not None or profile_name != "":
        _ensure_profile_directory()
        if not os.path.exists(_get_profiles_file_name(profile_name)):
            return ""

        with open(_get_profiles_file_name(profile_name), 'r', encoding="utf-8") as file:
            return file.read()


def save_profile(profile_name, profile_args):
    if profile_name is not None or profile_name != "":
        _ensure_profile_directory()
        with open(_get_profiles_file_name(profile_name), 'w', encoding="utf-8") as file:
            file.write(profile_args)
            file.close()


def delete_profile(profile_name):
    if profile_name is not None or profile_name != "":
        _ensure_profile_directory()
        profile_to_delete = _get_profiles_file_name(profile_name)
        if os.path.exists(profile_to_delete):
            os.remove(profile_to_delete)


def get_profile_names():
    _ensure_profile_directory()
    return list(map(lambda file: file.replace(_get_profile_directory() + os.sep, "").replace(".txt", ""),
                    _get_profile_files()))


def _get_profiles_file_name(profile_name):
    return _get_profile_directory() + os.sep + profile_name + ".txt"


def _get_profile_files():
    return glob.glob(_get_profile_directory() + os.sep + "*.txt")


def _ensure_profile(profile_name):
    _ensure_profile_directory()
    if not os.path.exists(_get_profiles_file_name(profile_name)):
        os.mkdir(_get_profile_directory())


def _ensure_profile_directory():
    if not os.path.exists(_get_profile_directory()):
        os.mkdir(_get_profile_directory())
    default_profile_file = _get_profiles_file_name("Default")
    if not os.path.exists(default_profile_file):
        with open(default_profile_file, 'w', encoding="utf-8") as file:
            file.write("--open -f=C:/path/to/my/images/*.* -od=C:/path/to/my/images/Compiled")
            file.close()


def ensure_directory(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)


def _ensure_config_directory():
    ensure_directory(_get_config_directory())
    full_path = _get_config_directory() + os.sep + cc_suite_config_file
    if not os.path.exists(full_path):
        with open(full_path, 'w', encoding="utf-8") as file:
            file.write(cc_suite_config_file_contents)
            file.close()


def get_cc_suite_config_file():
    _ensure_config_directory()
    return _get_config_directory() + os.sep + cc_suite_config_file


def _get_profile_directory():
    return _get_appdata_directory() + comicom_profiles_directory


def _get_config_directory():
    return _get_appdata_directory() + cc_suite_config_directory


def _get_appdata_directory():
    return os.getenv('APPDATA') + os.sep


cc_suite_config_file_contents = """
# Use this config file to control how you will download/compile comic series
# The [default] settings structure will apply to all series.
# You can add new [series] settings that override some (or all) of the defaults if you need them

[default]
# This is the full folder path of your system that you want all of CC-Suite 
working_directory=C:/CCSuite/
# Folder that will be created to store input/output images; If blank, will use the [shortkey]
folder_name=
# The url that you want to download your source images from (if download fails, program will stop)
# for supported sources, see: https://manga-py.com/manga-py/#resources-list
mangapy_source=
# The local path where you expect your input images to be (will ignore if you've included a mangapy_source)
local_input=C:/Users/YOUR_NAME/Downloads/*.jpg
# The local path where you've stored any ad files that you would like automatically removed from input images
ads_folder=
# The DeepAI API key required to use the online Waifu2x site (will waifu at 2x magnification and level 2 denoise)
# If no key is provided, the input images will not be waifu'd and the program will continue with compilation
# You will need to create an account and check your dashboard for your api key: https://deepai.org/dashboard/profile
waifu_key=
# Any additional arguments you want comicom.py to use (no need to set input/output values)
arguments=--info --open -m 1:10 -M 1:3 -bb 50%

# Example config format.... 
# Any arguments input here will override those found in [default]
[tst] 
folder_name=Testing
arguments=--debug
"""
