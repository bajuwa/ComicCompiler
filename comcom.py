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
                         "when an input image ends in a breakpoint colour. Mode 1 will scan through out the input "
                         "images to find a breakpoint.")
parser.add_argument("-bi", "--break-points-increment", default=10, type=int,
                    help="When in Breakpoint Detection Mode #1 this value controls how often the script tests a line "
                         "in an image file for a breakpoint.")
parser.add_argument("-bm", "--break-points-multiplier", default=20, type=int,
                    help="When in Breakpoint Detection Mode #1 this value controls how large of a vertical area is "
                         "pre-tested for a breakpoint before iterating over rows via Breakpoint Row Check Increments.")
parser.add_argument("-c", "--split-on-colour", default=[0, 65535], type=int, nargs="+",
                    help="The list of decimal notation colours you want to split on. Use 65535 for white, 0 for black, "
                         "or any number in that range for your intended colour.")
parser.add_argument("-C", "--additional-split-on-colour", default=[], type=int, nargs="+",
                    help="The list of decimal notation colours you want to split on in addition to the provided "
                         "defaults in SPLIT_ON_COLOUR.")
parser.add_argument("-ce", "--colour-error-tolerance", default=0, type=int,
                    help="The error tolerance used when testing whether a specific image/row matches the given "
                         "breakpoint colour")
parser.add_argument("-csd", "--colour-standard-deviation", default=0, type=int,
                    help="The maximum allowed standard deviation in colour values when testing for a breakpoint.")
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


def _get_input_images():
    _log_inline("Loading images")
    images = []
    image_paths = sorted(glob.glob((args.input_directory + args.input_file_prefix + "*" + args.extension)))
    for i in range(len(image_paths)):
        if i % 5 == 0:
            _log_progress()
        image = Image()
        image.path = image_paths[i]
        image.batch_index = i
        image.width = _get_image_width(image.path)
        image.height = _get_image_height(image.path)
        images.append(image)

    _log_inline("Loaded {img_count} images.".format(img_count=len(images)))
    _info("")
    return images


def run():
    if shutil.which("magick") is None:
        _info("Couldn't find ImageMagick via the 'magick' command")
        exit(1)

    if args.logging_level > 0:
        _debug("Running with args: %s" % args)
        _debug("")

    _info("Starting compilation...")
    start = time.time()

    # Get the images we need (based on args)
    images = _get_input_images()
    _verbose("Found images: " + " ".join(map(lambda image: str(image), images)))

    if len(images) == 0:
        _info("Couldn't find any images to combine")
        exit(1)

    _ensure_consistent_width(args.output_file_width, images)
    _ensure_directory(args.output_directory, args.clean)
    _combine_images(images)

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


def _log_level(level, message):
    if args.logging_level >= level:
        sys.stdout.write(message + "\n")
        sys.stdout.flush()


def _info(message):
    _log_level(0, message)


def _debug(message):
    _log_level(1, message)


def _verbose(message):
    _log_level(2, message)


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


# Try to avoid calling command other than imgmag ones in order to prevent cross-os problems
def _imgmag_command(command):
    _log_level(3, "Running command: " + command)
    process = subprocess.Popen(command, shell=True, close_fds=True, universal_newlines=True,
                               stdin=subprocess.PIPE, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    out, err = process.communicate()
    return out


def _imgmag_identify(params):
    return _imgmag_command("magick identify " + params)


def _imgmag_convert(params):
    return _imgmag_command("magick convert " + params)


def _get_image_width(image_path):
    return int(_imgmag_identify('-format "%w" ' + image_path))


def _get_image_height(image_path):
    return int(_imgmag_identify('-format "%h" ' + image_path))


def _get_image_gray_mean(image_path):
    return round(float(_imgmag_identify('-format %[mean] ' + image_path)))


def _get_image_standard_deviation(image_path):
    return round(float(_imgmag_identify('-format %[standard-deviation] ' + image_path)))


def _resize_width(target_width, image_path):
    _imgmag_convert("{file} -adaptive-resize {width}x {file}".format(file=image_path, width=target_width))
    pass


def _ensure_consistent_width(target_width, images):
    if target_width == 0:
        _debug("No given width, extracting first images width: %s " % images[0])
        target_width = images[0].width

    _info("Checking input images are target width: " + str(target_width))

    for image in images:
        if image.width != target_width:
            _verbose("File {file} not target width {target_width}, current width {current_width}"
                     .format(file=image.name, target_width=target_width, current_width=image.width))
            _resize_width(target_width, image.name)
            image.width = target_width

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


def ends_in_breakpoint(image):
    file_sample = "{file_name}[{width}x1+0+{height}]".format(file_name=image.path,
                                                             width=image.width,
                                                             height=image.height-1)
    gray_mean_value = _get_image_gray_mean(file_sample)
    standard_deviation = _get_image_standard_deviation(file_sample)

    for colour in args.split_on_colour:
        colour_difference = int(gray_mean_value) - int(colour)
        if abs(colour_difference) <= args.colour_error_tolerance \
                and standard_deviation <= args.colour_standard_deviation:
            _debug("Image {file_sample} ends in a breakpoint colour {colour}".format(file_sample=file_sample,
                                                                                     colour=colour))
            return True
        else:
            _verbose("Image {file_sample} does not end in a breakpoint colour {colour} (found gray mean value "
                     "{gray_mean} and standard deviation {standard_deviation})"
                     .format(file_sample=file_sample, colour=colour,
                             gray_mean=gray_mean_value, standard_deviation=standard_deviation))

    return False


def _define_page(page, images):
    _log_inline("Finding images to combine into '{0}'".format(page.name))

    for image in images:
        _log_progress()
        _verbose("Current image : " + str(image))

        page.add_image(image)

        # Check if totalHeight + thisImagesHeight > minRequiredHeight
        # If so, start looking for a breakpoint at the minRequiredHeight - totalHeight
        # Add next images height to the overall height
        # If a breakpoint found, store cropFromBottom + cropFromTop for later and break loop
        current_height = page.calculate_cropped_height()
        if current_height < args.min_height_per_page:
            _verbose("Haven't reach min page height {min_height}, current height: {current_height}"
                     .format(min_height=args.min_height_per_page, current_height=current_height))
            continue

        _debug("Reached min page height {min_height}, checking for breakpoint in {image}"
               .format(min_height=args.min_height_per_page, image=image.path))
        if args.breakpoint_detection_mode == 1:
            _log_inline("Searching for breakpoint in '{0}'".format(image.path))
            breakpoint_row = 200  # temp, should be: find_breakpoint(image)
            if breakpoint_row >= 0:
                page.crop_from_bottom = image.height - breakpoint_row
                return
        else:
            if ends_in_breakpoint(image):
                return
    pass


def _get_image_paths(images):
    return " ".join(map(lambda image: image.path, images))


def _stitch_page(page):
    _verbose("Stitching page: " + str(page))

    # -append           : will stitch together the images vertically
    # -colorspace sRGB  : prevents a single white/black image from making the whole page black/white
    _imgmag_convert("-append {images} -colorspace sRGB {output_dir}{page_name}".format(
        images=_get_image_paths(page.images), output_dir=args.output_directory, page_name=page.name))

    _log_inline("Combined {image_count} images into '{page_name}': {image_start} - {image_end}"
                .format(image_count=page.image_count(), page_name=page.name, image_start=page.get_first_image_index(),
                        image_end=page.get_last_image_index()))
    _info("")
    pass


def _crop_page(page):
    if page.crop_from_bottom == 0 and page.crop_from_top == 0:
        _verbose("No cropping occurred for " + page.name)
        pass

    _verbose("Cropping page: " + str(page))

    page_file_path = args.output_directory + page.name

    crop_sample_range = "{width}x{height}+0+{top_offset}".format(
        width=args.output_file_width, height=page.calculate_cropped_height(), top_offset=page.crop_from_top
    )
    _debug("Cropping: {file}[{sample}]".format(file=page_file_path, sample=crop_sample_range))
    _imgmag_convert("-crop {sample} {file} {file}".format(sample=crop_sample_range, file=page_file_path))
    pass


def _combine_images(images):
    image_index = 0
    total_image_count = len(images)
    pages = []

    # Log an empty line to allow the 'inline logging' to have a clean new line anchor
    _info("")

    while image_index < total_image_count:
        page = Page()
        page.name = "{prefix}{number:03d}{extension}".format(prefix=args.output_file_prefix,
                                                             number=args.output_file_starting_number + len(pages),
                                                             extension=args.extension)
        if len(pages) > 1:
            page.crop_from_top = pages[len(pages) - 1].crop_from_bottom
        pages.append(page)

        _define_page(page, images[image_index:])
        _stitch_page(page)
        _crop_page(page)

        image_index += page.image_count()

        if page.crop_from_bottom > 0:
            image_index -= 1

        _debug("")

    return pages


# Eventually get a proper document structure...?


class Image:
    def __init__(self):
        self.path = None
        self.batch_index = None
        self.width = None
        self.height = None

    def __str__(self):
        return "Image{" \
               "path = " + self.path + \
               ", batch_index = " + str(self.batch_index) + \
               ", width = " + str(self.width) + \
               ", height = " + str(self.height) + \
               "}"


class Page:
    def __init__(self):
        self.name = ""
        self.images = []
        self.crop_from_top = 0
        self.crop_from_bottom = 0

    def add_image(self, image: Image):
        self.images.append(image)
        pass

    def image_count(self):
        return len(self.images)

    def get_last_image(self):
        if self.image_count() > 0:
            return self.images[self.image_count() - 1]
        return None

    def get_first_image_index(self):
        if self.image_count() > 0:
            return self.images[0].batch_index
        return None

    def get_last_image_index(self):
        if self.image_count() > 0:
            return self.images[self.image_count()-1].batch_index
        return None

    def calculate_uncropped_height(self):
        return sum(map(lambda image: image.height, self.images))

    def calculate_cropped_height(self):
        return self.calculate_uncropped_height() - self.crop_from_bottom - self.crop_from_top

    def __str__(self):
        return "Page{" \
               "name = " + self.name + \
               ", image_count = " + str(self.image_count()) + \
               ", crop_from_top = " + str(self.crop_from_top) + \
               ", crop_from_bottom = " + str(self.crop_from_bottom) + \
               "}"


# Trigger the actual program....
run()
