import glob
import os


comicom_profiles_directory = "comicom_profiles"


def load_profile(profile_name):
    if profile_name is not None or profile_name != "":
        _ensure_profile_directory()
        if not os.path.exists(_get_profiles_file_name(profile_name)):
            return ""

        with open(_get_profiles_file_name(profile_name), 'r') as file:
            return file.read()


def save_profile(profile_name, profile_args):
    if profile_name is not None or profile_name != "":
        _ensure_profile_directory()
        with open(_get_profiles_file_name(profile_name), 'w') as file:
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
        with open(default_profile_file, 'w') as file:
            file.write("-l 0")
            file.close()


def _get_profile_directory():
    return os.getenv('APPDATA') + os.sep + comicom_profiles_directory
