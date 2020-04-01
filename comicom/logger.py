import sys


logging_level = 0
delete_line_string = "\r%b\033[2K"


def _log(message):
    sys.stdout.write(message + "\n")
    sys.stdout.flush()


def _log_level(level, message):
    if logging_level >= level:
        _log(message)


def info(message):
    _log_level(0, message)


def debug(message):
    _log_level(1, message)


def verbose(message):
    _log_level(2, message)


def inline(message):
    if logging_level == 0:
        sys.stdout.write(delete_line_string)

    sys.stdout.write(message)

    if logging_level >= 1:
        sys.stdout.write("\n")

    sys.stdout.flush()


def inline_progress():
    if logging_level == 0:
        sys.stdout.write(".")
        sys.stdout.flush()
