import os
import tempfile
import time
import shutil
import glob
import natsort

from . import imgmag
from . import entities
from . import logger


image_magick_error = "Couldn't find ImageMagick via the 'magick' command.\n" \
                     "ImageMagick version 7+ can be installed from: \n" \
                     "https://imagemagick.org/script/download.php \n\n" \
                     "After installing, make sure to close and reopen Comic Compiler before trying again."


def run(args):
    logger.logging_level = args.logging_level

    if shutil.which("magick") is None:
        logger.info(image_magick_error)
        return

    logger.debug("Running with args: %s" % args)
    logger.debug("")

    logger.info("Starting compilation...")
    start = time.time()

    # Get the images we need (based on args)
    images = _get_input_images(args.input_files, not args.disable_input_sort)

    if len(images) == 0:
        logger.info("Couldn't find any images to combine")
        return

    temp_directory = tempfile.mkdtemp(prefix="comicom")
    _ensure_consistent_width(args.output_file_width, images, temp_directory)

    if args.enable_stitch_check:
        found_mismatch = False
        logger.info("Checking to make sure input image connections match...")
        for index in range(0, len(images)-1):
            if check_stitch_connections_match(images[index], images[index + 1]):
                found_mismatch = True
        if found_mismatch:
            shutil.rmtree(temp_directory)
            return

    _ensure_directory(args.output_directory, args.clean)
    _combine_images(images, args.output_directory, args.output_file_prefix, args.output_file_starting_number,
                    args.extension, args.min_height_per_page, args.output_file_width, args.breakpoint_detection_mode,
                    args.break_points_increment, args.break_points_multiplier, args.split_on_colour,
                    args.colour_error_tolerance, args.colour_standard_deviation)

    shutil.rmtree(temp_directory)

    end = time.time()
    total_time = end - start
    logger.info("")
    logger.info("Comic Compilation - Complete! (time: %ds)" % total_time)

    if args.open:
        if args.output_directory.startswith("./"):
            os.startfile(os.path.dirname(os.path.realpath('__file__')) + args.output_directory[1:])
        else:
            os.startfile(args.output_directory)

    if args.exit:
        input("Press enter to exit")
        logger.info("")
    pass


def _get_input_images(input_file_patterns, enable_input_sort):
    logger.verbose("Getting images that match patterns: " +
                   " ".join(map(lambda image: str(image), input_file_patterns)))
    logger.inline("Loading images")
    image_paths = []
    for input_file_pattern in input_file_patterns:
        image_paths += glob.glob(input_file_pattern)
    if enable_input_sort:
        image_paths = natsort.natsorted(image_paths)
    logger.verbose("Image paths: " + str(image_paths))

    images = []
    for i in range(len(image_paths)):
        if i % 5 == 0:
            logger.inline_progress()
        image = entities.Image()
        image.path = image_paths[i]
        image.batch_index = i
        image.width = imgmag.get_image_width(image.path)
        image.height = imgmag.get_image_height(image.path)
        images.append(image)

    logger.verbose("Found images: " + " ".join(map(lambda image: str(image), images)))
    logger.inline("Loaded {img_count} images.".format(img_count=len(images)))
    logger.info("")
    return images


def _copy_to_temp(path, temp_directory):
    if not os.path.exists(temp_directory):
        os.mkdir(temp_directory)
    return shutil.copy2(path, temp_directory)


def _ensure_consistent_width(target_width, images, temp_directory):
    if target_width == 0:
        logger.debug("No given width, extracting first images width: %s " % images[0])
        target_width = images[0].width

    logger.info("Checking input images are target width: " + str(target_width))

    for image in images:
        if image.width != target_width:
            logger.verbose("File {file} not target width {target_width}, current width {current_width}"
                           .format(file=image.path, target_width=target_width, current_width=image.width))
            image.path = _copy_to_temp(image.path, temp_directory)
            imgmag.resize_width(target_width, image.path)
            image.width = imgmag.get_image_width(image.path)
            image.height = imgmag.get_image_height(image.path)

    pass


def check_stitch_connections_match(prev_image, next_image):
    prev_image_sample = imgmag.get_file_sample_string(prev_image.path, width=prev_image.width, y_offset=prev_image.height-1)
    next_image_sample = imgmag.get_file_sample_string(next_image.path, width=next_image.width)
    if not imgmag.almost_matches(prev_image_sample, next_image_sample):
        logger.info("[ERROR] Two consecutive images do not appear to end/start with the same colours/pattern, "
                    "check to make sure you're not missing an image or are including title/credit pages\n"
                    "First image: {}\n"
                    "Second image: {}"
                    .format(prev_image.path, next_image.path))
        return True
    return False


def _ensure_directory(output_directory, clean):
    if clean and os.path.exists(output_directory):
        shutil.rmtree(output_directory)
        # We have to wait for rmtree to properly finish before trying to mkdir again
        while os.path.exists(output_directory):
            continue
        time.sleep(0.5)

    if not os.path.exists(output_directory):
        os.mkdir(output_directory)

    pass


def _find_breakpoint(page, image, min_height_per_page, break_points_increment, break_points_multiplier, split_on_colour,
                     colour_error_tolerance, colour_standard_deviation):
    excess_height = page.calculate_uncropped_height() - page.crop_from_top - min_height_per_page
    offset = image.height - excess_height
    batch_sample_size = break_points_increment * break_points_multiplier
    return imgmag.find_solid_row_of_colour(image, max(0, offset), batch_sample_size, break_points_increment,
                                           split_on_colour, colour_error_tolerance, colour_standard_deviation)


def _define_page(page, images, min_height_per_page, breakpoint_detection_mode, split_on_colour,
                 colour_error_tolerance, colour_standard_deviation, break_points_increment,
                 break_points_multiplier):
    logger.inline("Finding images to combine into '{0}'".format(page.name))

    for image in images:
        logger.inline_progress()
        logger.verbose("Current image : " + str(image))

        page.add_image(image)

        # should probably look at having this be the area for 'orphan adoption'
        if image == images[len(images) - 1]:
            continue

        # Check if totalHeight + thisImagesHeight > minRequiredHeight
        # If so, start looking for a breakpoint at the minRequiredHeight - totalHeight
        # Add next images height to the overall height
        # If a breakpoint found, store cropFromBottom + cropFromTop for later and break loop
        current_height = page.calculate_cropped_height()
        if current_height < min_height_per_page:
            logger.verbose("Haven't reach min page height {min_height}, current height: {current_height}"
                           .format(min_height=min_height_per_page, current_height=current_height))
            continue

        logger.debug("Reached min page height {min_height}, checking for breakpoint in {image}"
                     .format(min_height=min_height_per_page, image=image.path))
        if breakpoint_detection_mode == 1:
            logger.inline("Searching for breakpoint in '{0}'".format(image.path))
            breakpoint_row = _find_breakpoint(page, image, min_height_per_page, break_points_increment,
                                              break_points_multiplier, split_on_colour, colour_error_tolerance,
                                              colour_standard_deviation)
            if breakpoint_row >= 0:
                page.crop_from_bottom = image.height - breakpoint_row
                return
        else:
            if imgmag.image_bottom_row_is_colour(image, split_on_colour, colour_error_tolerance,
                                                 colour_standard_deviation):
                return
    pass


def _get_image_paths(images):
    return list(map(lambda image: image.path, images))


def _stitch_page(page, output_directory):
    logger.verbose("Stitching page: " + str(page))

    imgmag.combine_vertically(_get_image_paths(page.images), output_directory + page.name)

    logger.inline("Combined {image_count} images into '{page_name}': {image_start} - {image_end}"
                  .format(image_count=page.image_count(), page_name=page.name, image_start=page.get_first_image_index(),
                          image_end=page.get_last_image_index()))
    logger.info("")
    pass


def _crop_page(page, output_file_width, output_directory):
    if page.crop_from_bottom == 0 and page.crop_from_top == 0:
        logger.verbose("No cropping occurred for " + page.name)
        return

    logger.verbose("Cropping page: " + str(page))

    imgmag.crop_in_place(output_directory + page.name, output_file_width, page.calculate_cropped_height(),
                         page.crop_from_top)


def _combine_images(images, output_directory, output_file_prefix, output_file_starting_number, extension,
                    min_height_per_page, output_file_width, breakpoint_detection_mode, break_points_increment,
                    break_points_multiplier, split_on_colour, colour_error_tolerance, colour_standard_deviation):
    image_index = 0
    total_image_count = len(images)
    pages = []

    # Log an empty line to allow the 'inline logging' to have a clean new line anchor
    logger.info("")

    while image_index < total_image_count:
        page = entities.Page()
        page.name = "{prefix}{number:03d}{extension}".format(prefix=output_file_prefix,
                                                             number=output_file_starting_number + len(pages),
                                                             extension=extension)
        if len(pages) > 0:
            previous_page = pages[len(pages) - 1]
            if previous_page.crop_from_bottom > 0:
                page.crop_from_top = previous_page.get_last_image().height - previous_page.crop_from_bottom

        pages.append(page)

        _define_page(page, images[image_index:], min_height_per_page, breakpoint_detection_mode, split_on_colour,
                     colour_error_tolerance, colour_standard_deviation, break_points_increment, break_points_multiplier)
        _stitch_page(page, output_directory)
        _crop_page(page, output_file_width, output_directory)

        image_index += page.image_count()

        if page.crop_from_bottom > 0:
            image_index -= 1

        logger.debug("")

    return pages
