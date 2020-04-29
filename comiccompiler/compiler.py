import os
import tempfile
import time
import shutil
import glob
import natsort
import re

from PIL import Image

from . import imgmag
from . import arguments
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

    try:
        if not _pre_process_images(images, temp_directory, args.enable_stitch_check, args.output_file_width):
            _cleanup(images, temp_directory)
            return

        _ensure_directory(args.output_directory, args.clean)

        min_pixel_height_per_page = _recalculate_height_relative_to_images(str(args.min_height_per_page), images)
        min_pixel_height_last_page = _recalculate_height_relative_to_images(str(args.min_height_last_page), images)

        if args.breakpoint_detection_mode < 0:
            args.breakpoint_detection_mode = _predict_appropriate_breakpoint_mode(images,
                                                                                  min_pixel_height_per_page,
                                                                                  args.split_on_colour,
                                                                                  args.colour_error_tolerance,
                                                                                  args.colour_standard_deviation)

        pages = _combine_images(images, args.output_directory, args.output_file_prefix,
                                args.output_file_starting_number, args.extension, min_pixel_height_per_page,
                                args.output_file_width, args.breakpoint_detection_mode, args.breakpoint_buffer,
                                args.break_points_increment, args.break_points_multiplier, args.split_on_colour,
                                args.colour_error_tolerance, args.colour_standard_deviation)

        _post_process_pages(pages, min_pixel_height_per_page)
        _handle_potential_orphan_page(pages, args.output_directory, min_pixel_height_last_page)

        if args.open:
            if args.output_directory.startswith("./"):
                os.startfile(os.path.dirname(os.path.realpath('__file__')) + args.output_directory[1:])
            else:
                os.startfile(args.output_directory)
    finally:
        _cleanup(images, temp_directory)

    end = time.time()
    total_time = end - start
    logger.info("")
    logger.info("Comic Compilation - Complete! (time: %ds)" % total_time)

    if args.exit:
        input("Press enter to exit")
        logger.info("")
    pass


def _cleanup(images, temp_directory):
    for image in images:
        image.close()
    if os.path.exists(temp_directory):
        shutil.rmtree(temp_directory)


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

        try:
            image = Image.open(image_paths[i])
            image.info["batch_index"] = i
            image.info["path"] = image_paths[i]
            images.append(image)
        except IOError:
            logger.warn("Found input file that was not an image, skipping: " + image_paths[i])
            continue

    logger.verbose("Found images: " + " ".join(map(lambda image: image.info["path"], images)))
    logger.inline("Loaded {img_count} images.".format(img_count=len(images)))
    logger.info("")
    return images


def _pre_process_images(images, temp_directory, enable_stitch_check, output_file_width):
    succeeded = True

    _ensure_consistent_width(output_file_width, images, temp_directory)

    if enable_stitch_check:
        logger.info("Checking to make sure input image connections match...")
        for index in range(0, len(images)-1):
            if check_stitch_connections_match(images[index], images[index + 1]):
                succeeded = False

    return succeeded


def _copy_to_temp(path, temp_directory):
    if not os.path.exists(temp_directory):
        os.mkdir(temp_directory)
    return shutil.copy2(path, temp_directory)


def _ensure_consistent_width(target_width, images, temp_directory):
    if target_width == 0:
        logger.debug("No given width, extracting first images width: %s " % images[0].info["path"])
        target_width = images[0].width

    logger.info("Checking input images are target width: " + str(target_width))

    for i in range(0, len(images)):
        image = images[i]
        if image.width != target_width:
            logger.warn("File {file} not target width {target_width}, current width {current_width}, resizing..."
                        .format(file=image.info["path"], target_width=target_width, current_width=image.width))
            old_image_info = image.info.copy()
            image.close()
            new_path = _copy_to_temp(image.info["path"], temp_directory)
            imgmag.resize_width(target_width, new_path)
            images[i] = Image.open(new_path)
            images[i].info = old_image_info
            images[i].info["path"] = new_path
            logger.debug("Resized file: " + images[i].info["path"])

    pass


def _predict_appropriate_breakpoint_mode(images, min_height_per_page, split_on_colour, colour_error_tolerance,
                                         colour_standard_deviation):
    logger.info("Predicting appropriate breakpoint mode...")
    heights_between_file_end_breakpoints = [0]
    for image in images:
        heights_between_file_end_breakpoints[-1] += image.height
        if imgmag.image_bottom_row_is_colour(image, split_on_colour, colour_error_tolerance, colour_standard_deviation):
            heights_between_file_end_breakpoints += [0]
            image.info["ends in breakpoint"] = True
        else:
            image.info["ends in breakpoint"] = False

    avg_height_per_page = sum(heights_between_file_end_breakpoints) / len(heights_between_file_end_breakpoints)
    logger.verbose("total list: " + str(heights_between_file_end_breakpoints))
    logger.verbose("avg height per page: " + str(avg_height_per_page))
    if avg_height_per_page > 0.67 * min_height_per_page:
        logger.info("Breakpoint mode: Dynamic Search")
        logger.debug("(average height between file endings too long)")
        return 1
    elif max(heights_between_file_end_breakpoints) >= min_height_per_page:
        logger.info("Breakpoint mode: Dynamic Search")
        logger.debug("(single page too long if only using file endings)")
        return 1
    else:
        logger.info("Breakpoint mode: End of File")
        return 0


def _recalculate_height_relative_to_images(min_height_per_page, images):
    if arguments.matches(min_height_per_page, arguments.pattern_pixels):
        return int(re.sub(r"\D", "", min_height_per_page))

    if arguments.matches(min_height_per_page, arguments.pattern_ratio):
        (width, height) = min_height_per_page.split(":")
        multiplier_of_width = int(height) / int(width)
        return images[0].width * multiplier_of_width

    total_image_height = sum(list(map(lambda image: image.height, images)))
    percent_of_total_height = 1.0

    if arguments.matches(min_height_per_page, arguments.pattern_percent):
        percent_of_total_height = float(min_height_per_page.strip('%')) / 100.0

    if arguments.matches(min_height_per_page, arguments.pattern_fraction):
        (width, height) = min_height_per_page.split("/")
        percent_of_total_height = int(width) / int(height)

    return int(total_image_height * percent_of_total_height)


def check_stitch_connections_match(prev_image, next_image):
    prev_image_sample = imgmag.get_file_sample_string(prev_image.info["path"], width=prev_image.width, y_offset=prev_image.height-1)
    next_image_sample = imgmag.get_file_sample_string(next_image.info["path"], width=next_image.width)
    if not imgmag.almost_matches(prev_image_sample, next_image_sample):
        logger.error("Two consecutive images do not appear to end/start with the same colours/pattern, "
                     "check to make sure you're not missing an image or are including title/credit pages\n"
                     "First image: {}\n"
                     "Second image: {}"
                     .format(prev_image.info["path"], next_image.info["path"]))
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


def _find_breakpoint(page, image, min_height_per_page, breakpoint_buffer, break_points_increment,
                     break_points_multiplier, split_on_colour, colour_error_tolerance, colour_standard_deviation):
    excess_height = page.calculate_uncropped_height() - page.crop_from_top - min_height_per_page
    offset = int(image.height - excess_height)
    batch_sample_size = int(break_points_increment * break_points_multiplier)

    if "%" in breakpoint_buffer:
        max_range = image.height
    else:
        max_range = int(breakpoint_buffer.strip("px"))

    (start, end) = imgmag.find_consecutive_rows_of_colour(image, max(0, offset), batch_sample_size,
                                                          break_points_increment, max_range, split_on_colour,
                                                          colour_error_tolerance, colour_standard_deviation)

    if "%" in breakpoint_buffer:
        buffer_percent = int(breakpoint_buffer.strip("%")) / 100.0
        return int(start + (end - start) * buffer_percent)
    else:
        buffer_pixel = int(breakpoint_buffer.strip("px"))
        return min(start + buffer_pixel, end)


def _define_page(page, images, min_height_per_page, breakpoint_detection_mode, breakpoint_buffer, split_on_colour,
                 colour_error_tolerance, colour_standard_deviation, break_points_increment,
                 break_points_multiplier):
    logger.inline("Finding images to combine into '{0}'".format(page.name))

    for image in images:
        logger.inline_progress()
        logger.verbose("Current image : " + image.info["path"])

        page.add_image(image)

        # should probably look at having this be the area for 'orphan adoption'
        if image.info["path"] == images[len(images) - 1].info["path"]:
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
                     .format(min_height=min_height_per_page, image=image.info["path"]))
        if breakpoint_detection_mode == 1:
            logger.inline("Searching for breakpoint in '{0}'".format(image.info["path"]))
            breakpoint_row = _find_breakpoint(page, image, min_height_per_page, breakpoint_buffer,
                                              break_points_increment, break_points_multiplier, split_on_colour,
                                              colour_error_tolerance, colour_standard_deviation)
            if breakpoint_row >= 0:
                page.crop_from_bottom = image.height - breakpoint_row
                return
        else:
            if "ends in breakpoint" in image.info:
                ends_in_breakpoint = image.info["ends in breakpoint"]
                logger.verbose("'File ends breakpoint' already known: " + str(ends_in_breakpoint))
                if ends_in_breakpoint:
                    return
            elif imgmag.image_bottom_row_is_colour(image, split_on_colour, colour_error_tolerance,
                                                   colour_standard_deviation):
                return
    pass


def _get_image_paths(images):
    return list(map(lambda image: image.info["path"], images))


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
                    min_height_per_page, output_file_width, breakpoint_detection_mode, breakpoint_buffer,
                    break_points_increment, break_points_multiplier, split_on_colour, colour_error_tolerance,
                    colour_standard_deviation):
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

        _define_page(page, images[image_index:], min_height_per_page, breakpoint_detection_mode, breakpoint_buffer,
                     split_on_colour, colour_error_tolerance, colour_standard_deviation, break_points_increment,
                     break_points_multiplier)
        _stitch_page(page, output_directory)
        _crop_page(page, output_file_width, output_directory)

        image_index += page.image_count()

        if page.crop_from_bottom > 0:
            image_index -= 1

        logger.debug("")

    return pages


def _post_process_pages(pages, expected_min_height):
    trigger_warning = False
    max_height_to_warn = expected_min_height * 1.8
    for page in pages:
        if page.calculate_cropped_height() >= max_height_to_warn:
            trigger_warning = True
    if trigger_warning:
        logger.warn("Seems like you've got some pages that are much longer than your configured minimum "
                    "height.  Check out our wiki's FAQ for ways to fix this\n"
                    "https://github.com/bajuwa/ComicCompiler/wiki/Tutorial:-FAQ#troubleshooting-compiled-pages")


def _handle_potential_orphan_page(pages, output_directory, expected_min_height_last_page):
    if len(pages) > 1 and pages[-1].calculate_cropped_height() < expected_min_height_last_page:
        logger.info("Last page was too short, combining in to the previous page.")
        image_paths = list(map(lambda page: output_directory + page.name, pages[-2:]))
        imgmag.combine_vertically(image_paths, image_paths[-2])
        os.remove(image_paths[-1])
