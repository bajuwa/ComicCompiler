import sys


logging_level = 2
delete_line_string = "\r%b\033[2K"


def _supports_inline_logging():
    return 1 <= logging_level <= 2


def _log(message):
    sys.stdout.write(message + "\n")
    sys.stdout.flush()


def _log_level(level, message):
    if logging_level >= level:
        _log(message)


def error(message):
    _log_level(0, "[ERROR] " + message)


def info(message):
    _log_level(1, message)


def warn(message):
    _log_level(2, "[WARN] " + message)


def debug(message):
    _log_level(3, "[DEBUG] " + message)


def verbose(message):
    _log_level(4, "[VERBOSE] " + message)


def inline(message):
    if logging_level < 1:
        return

    if _supports_inline_logging():
        sys.stdout.write(delete_line_string)

    sys.stdout.write(message)

    if not _supports_inline_logging():
        sys.stdout.write("\n")

    sys.stdout.flush()


def inline_progress():
    if _supports_inline_logging():
        sys.stdout.write(".")
        sys.stdout.flush()
