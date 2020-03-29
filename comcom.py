#!/usr/bin/python

import argparse
import glob
import os
import sys
import subprocess
import time
import shutil

parser = argparse.ArgumentParser(description="Given a set of images, vertically combines them in to 'pages' where the "
                                             "start/end of the page are solid white (or some other specified colour).")

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


def run():
    if shutil.which("magick") is None:
        _info("Couldn't find ImageMagick via the 'magick' command")
        exit(1)

    if args.logging_level > 0:
        _debug("Running with args: %s" % args)
        _debug("")

    input_images = sorted(glob.glob((args.input_directory + args.input_file_prefix + "*" + args.extension)))
    _verbose("Found images: " + str(input_images))

    if len(input_images) == 0:
        _info("Couldn't find any images to combine")
        exit(1)

    _info("Starting compilation...")
    start = time.time()
    _ensure_directory(args.output_directory, args.clean)
    _ensure_consistent_width(args.output_file_width, input_images)
    _combine_images(input_images)
    end = time.time()
    total_time = end - start
    _info("Comic Compilation - Complete! (time: %ds)" % total_time)

    if args.open:
        os.system("explorer . &")

    if args.exit:
        input("Press enter to exit")
        _info("")
    pass


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


def _log_inline(message):
    if args.logging_level == 0:
        sys.stdout.write("\r%b\033[2K")

    sys.stdout.write(message)

    if args.logging_level >= 1:
        sys.stdout.write("\n")

    sys.stdout.flush()


def _log_progress():
    if args.logging_level == 0:
        sys.stdout.write(".")
        sys.stdout.flush()


# Possible to do the 'erase line and reprint' logging?

# Eventually get a proper document structure...?

# Need to redesign how the data should be gathered/passed around (global vars are bad)

# Object for 'Page' that contains:
#   - ordered image file names to combine
#   - cumulativePageHeight
#   - crop values

# Try to avoid calling command other than imgmag ones in order to prevent cross-os problems
def _imgmag_command(command):
    _verbose("Running command: " + command)
    process = subprocess.Popen(command, shell=True, close_fds=True, universal_newlines=True,
                               stdin=subprocess.PIPE, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    out, err = process.communicate()
    return out


def _imgmag_identify(params):
    return _imgmag_command("identify " + params)


def _imgmag_convert(params):
    return _imgmag_command("convert " + params)


def _get_image_width(image_path):
    return int(_imgmag_identify('-format "%w" ' + image_path))


def _get_image_height(image_path):
    return int(_imgmag_identify('-format "%h" ' + image_path))


def _resize_width(target_width, image_path):
    _imgmag_convert("{file} -adaptive-resize {width}x {file}".format(file=image_path, width=target_width))
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
            continue

    if not os.path.exists(output_directory):
        os.mkdir(output_directory)

    pass


def _create_blank_page(page_index, image_index_offset):
    blank_page = Page()
    blank_page.name = "{prefix}{number:03d}{extension}".format(prefix=args.output_file_prefix, number=page_index,
                                                         extension=args.extension)
    blank_page.image_index_offset = image_index_offset
    return blank_page


def _populate_previous_page(page, previous_page):
    if previous_page.crop_from_bottom > 0:
        page.crop_from_top = previous_page.crop_from_bottom
        if previous_page.image_count > 0:
            page.add_image(previous_page.get_last_image)
    pass


def _define_page(page, input_images):
    _log_inline("Finding images to combine into '{0}'".format(page.name))
    page.add_image(input_images[0]) # temp for debugging, fill in later
    _log_progress()
    _log_progress()
    _log_progress()
    _log_progress()
    _log_progress()
    _log_progress()
    _log_progress()
    _log_progress()
    pass


def _stitch_page(page):
    _verbose("Stitching page: " + str(page))

    # -append           : will stitch together the images vertically
    # -colorspace sRGB  : prevents a single white/black image from making the whole page black/white
    _imgmag_convert("-append {images} -colorspace sRGB {output_dir}{page_name}"
                    .format(images=" ".join(page.images), output_dir=args.output_directory, page_name=page.name))

    image_index_end = (page.image_index_offset + page.image_count() - 1)
    _log_inline("Combined {image_count} images into '{page_name}': {image_start} - {image_end}"
                .format(image_count=page.image_count(), page_name=page.name, image_start=page.image_index_offset,
                        image_end=image_index_end))
    _info("")
    pass


def _crop_page(page):
    if page.crop_from_bottom == 0 and page.crop_from_top == 0:
        _verbose("No cropping occurred for " + page.name)
        pass

    _verbose("Cropping page: " + str(page))

    page_file_path = args.output_directory + page.name
    page_total_height = _get_image_height(page_file_path)
    page_cropped_height = page_total_height - page.crop_from_top - page.crop_from_bottom

    _verbose("page_total_height: " + str(page_total_height))
    _verbose("page_cropped_height: " + str(page_cropped_height))

    crop_sample_range = "{width}x{height}+0+{top_offset}".format(
        width=args.output_file_width, height=page_cropped_height, top_offset=page.crop_from_top
    )
    _debug("Cropping: {file}[{sample}]".format(file=page_file_path, sample=crop_sample_range))
    _imgmag_convert("-crop {sample} {file} {file}".format(sample=crop_sample_range, file=page_file_path))
    pass


def _combine_images(input_images):
    image_index = 0
    total_image_count = len(input_images)
    pages = []

    # Log an empty line to allow the 'inline logging' to have a clean new line anchor
    _info("")

    while image_index < total_image_count:
        page = _create_blank_page(args.output_file_starting_number + len(pages), image_index)
        if len(pages) > 1:
            _populate_previous_page(page, pages[len(pages)-1])
        pages.append(page)

        _define_page(page, input_images[image_index:])
        _stitch_page(page)
        _crop_page(page)

        image_index += page.image_count()

        if page.crop_from_bottom > 0:
            image_index -= 1

        _debug("")

    return pages

# Complex functions to port
#   fileSampleContainsColour
#   fileEndsInBreakPoint
#   findBreakPoint


class Page:
    def __init__(self):
        self.name = ""
        self.images = []
        self.image_index_offset = 0
        self.crop_from_top = 0
        self.crop_from_bottom = 0

    def add_image(self, image_path):
        self.images.append(image_path)
        pass

    def image_count(self):
        return len(self.images)

    def get_last_image(self):
        if self.image_count() > 0:
            return self.images[self.image_count() - 1]
        return None

    def __str__(self):
        return "Page{" \
               "name = " + self.name + \
               ", image_count = " + str(self.image_count()) + \
               ", image_index_offset = " + str(self.image_index_offset) + \
               ", crop_from_top = " + str(self.crop_from_top) + \
               ", crop_from_bottom = " + str(self.crop_from_bottom) + \
               "}"


# Trigger the actual program....
run()
