#!/usr/bin/python

import argparse
import glob
import os
import sys
import subprocess
import time
import shutil


def _log(message):
    sys.stdout.write(message + "\n")
    sys.stdout.flush()


def _info(message):
    _log(message)


def _debug(message):
    if args.logging_level >= 1:
        _log(message)


def _verbose(message):
    if args.logging_level >= 2:
        _log(message)


programDescription = "Given a set of images, vertically combines them in to 'pages' where the start/end of the page " \
                     "are solid white (or some other specified colour)."
parser = argparse.ArgumentParser(description=programDescription)

parser.add_argument("-m", "--min-height-per-page", default=5000, type=int,
                    help="The minimum allowed pixel height for each output page")
# parser.add_argument("-M", "--max-height-per-page", default=15000, type=int,
#                     help="The maximum allowed pixel height for each output page")
parser.add_argument("-i", "--input-file-prefix", default="image", type=str,
                    help="Will only combine images that start with this text")
parser.add_argument("-e", "--extension", default=".jpg", type=str,
                    help="The file extension of your input images and your output page files.")
parser.add_argument("-o", "--output-file-prefix", default="page", type=str,
                    help="The text that will go at the start of each output page name prior to the 3 digit zero "
                         "padded page number.")
parser.add_argument("-osn", "--output-file-starting-number", default=1, type=int,
                    help="The number of the first output page.")
parser.add_argument("-ow", "--output-file-width", default=0, type=int,
                    help="The explicit width of the output pages. If no value is given, or a value of 0 is given, "
                         "then the output pages will be the same width as the first input image.")
parser.add_argument("-id", "--input-directory", default="./", type=str,
                    help="The path to the directory you want to collect image files from.")
parser.add_argument("-is", "--include-sub-directories",
                    help="This will include images in subdirectories.")
parser.add_argument("-od", "--output-directory", default="./Compiled/", type=str,
                    help="The path to the directory you want to put the new page files in.")
parser.add_argument("-b", "--breakpoint-detection-mode", default=0, type=int,
                    help="The 'mode' that the script uses to detect where to split up pages. Mode 0 will split pages "
                         "when an input image ends in a breakpoint colour. Mode 1 will scan throughtout the input "
                         "images to find a breakpoint.")
parser.add_argument("-bi", "--break-points-increment", default=10, type=int,
                    help="When in Breakpoint Detection Mode #1 this value controls how often the script tests a line "
                         "in an image file for a breakpoint.")
parser.add_argument("-bm", "--break-points-multiplier", default=20, type=int,
                    help="When in Breakpoint Detection Mode #1 this value controls how large of a vertical area is "
                         "pre-tested for a breakpoint before iterating over rows via Breakpoint Row Check Increments.")
parser.add_argument("-c", "--split-on-colour", default=[0, 65355], type=int, nargs="+",
                    help="The list of decimal notation colours you want to split on. Use 65535 for white, 0 for black, "
                         "or any number in that range for your intended colour.")
parser.add_argument("-C", "--additional-split-on-colour", default=[], type=int, nargs="+",
                    help="The list of decimal notation colours you want to split on in addition to the provided "
                         "defaults in SPLIT_ON_COLOUR.")
parser.add_argument("-ce", "--colour-error-tolerance", default=0, type=int,
                    help="The error tolerance used when testing whether a specific image/row matches the given "
                         "breakpoint colour")
parser.add_argument("--exit", action="store_true",
                    help="If set, when the program finishes compiling it will prompt you to press enter before "
                         "terminating itself.")
parser.add_argument("--clean", action="store_true",
                    help="If set, before the new pages are compiled the program will delete the configured output "
                         "directory.")
parser.add_argument("--open", action="store_true",
                    help="If set, after the new pages are compiled the program will open the directory it was working "
                         "in via windows explorer.")

parser.add_argument("-l", "--logging-level", default=0, type=int,
                    help="Sets logging level [0 for basic, 1 for debug, 2 for verbose]")
parser.add_argument("--debug", action="store_true", help="Turns on debug level logging")
parser.add_argument("--verbose", action="store_true", help="Turns on verbose level logging")

args = parser.parse_args()

args.split_on_colour += args.additional_split_on_colour
if args.debug:
    args.logging_level = 1
if args.verbose:
    args.logging_level = 2

if args.logging_level > 0:
    _info("Running with args: %s" % args)
    _info("")


# Possible to do the 'erase line and reprint' logging?

# Eventually get a proper document structure...?

# Need to redesign how the data should be gathered/passed around (global vars are bad)

# Object for 'Page' that contains:
#   - ordered image file names to combine
#   - cumulativePageHeight
#   - crop values


def command(shell_command):
    process = subprocess.Popen(shell_command, shell=True, close_fds=True, universal_newlines=True,
                     stdin=subprocess.PIPE, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    out, err = process.communicate()
    return out


def _get_image_width(image_path):
    return command('identify -format "%w" ' + image_path)


def _resize_width(target_width, image_path):
    command("convert {file} -adaptive-resize {width}x {file}".format(file=image_path, width=target_width))
    pass


def _ensure_consistent_width(target_width, image_paths):
    if target_width == 0:
        _debug("No given width, extracting first images width: %s " % image_paths[0])
        target_width = _get_image_width(image_paths[0])

    _info("Checking input images are target width: " + str(target_width))

    for image_path in image_paths:
        current_width = _get_image_width(image_path)
        if current_width != target_width:
            _verbose("File {file} not target width {target_width}, current width {current_width}"
                     .format(file=image_path, target_width=target_width, current_width=current_width))
            _resize_width(target_width, image_path)

    pass


def _ensure_directory(output_directory, clean):
    if clean and os.path.exists(output_directory):
        shutil.rmtree(output_directory)
        # We have to wait for rmtree to properly finish before trying to mkdir again
        while os.path.exists(output_directory):
            pass

    if not os.path.exists(output_directory):
        os.mkdir(output_directory)

    pass


# Complex functions to port
#   fileSampleContainsColour
#   fileEndsInBreakPoint
#   findBreakPoint
#   cropFromTopAndBottom
#   findBatchSizeForNextPage
#   combineImages


# The actual program....

if shutil.which("magick") is None:
    _info("Couldn't find ImageMagick via the 'magick' command")
    exit(1)

input_images = sorted(glob.glob((args.input_directory + args.input_file_prefix + "*" + args.extension)))

if len(input_images) == 0:
    _info("Couldn't find any images to combine")
    exit(1)

_info("Starting compilation...")
start = time.time()
_ensure_directory(args.output_directory, args.clean)
_ensure_consistent_width(args.output_file_width, input_images)
# combineImages;
end = time.time()
totalTime = end - start
_info("Comic Compilation - Complete! (time: %ds)" % totalTime)

if args.open:
    os.system("explorer . &")

if args.exit:
    input("Press enter to exit")
    _info("")
