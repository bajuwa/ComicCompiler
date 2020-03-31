import subprocess

from . import logger


# Try to avoid calling command other than imgmag ones in order to prevent cross-os problems
def _command(command):
    # print("Running command: " + command)
    process = subprocess.Popen(command, shell=True, close_fds=True, universal_newlines=True,
                               stdin=subprocess.PIPE, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    out, err = process.communicate()
    return out


def _identify(params):
    return _command("magick identify " + params)


def _convert(params):
    return _command("magick convert " + params)


def get_image_width(image_path):
    return int(_identify('-format "%w" ' + image_path))


def get_image_height(image_path):
    return int(_identify('-format "%h" ' + image_path))


def get_image_gray_min(image_path):
    return round(float(_identify('-format %[min] ' + image_path)))


def get_image_gray_mean(image_path):
    return round(float(_identify('-format %[mean] ' + image_path)))


def get_image_gray_max(image_path):
    return round(float(_identify('-format %[max] ' + image_path)))


def get_image_standard_deviation(image_path):
    return round(float(_identify('-format %[standard-deviation] ' + image_path)))


def resize_width(target_width, image_path):
    _convert("{file} -adaptive-resize {width}x {file}".format(file=image_path, width=target_width))
    pass


def combine_vertically(input_image_paths, output_image_path):
    # -append           : will stitch together the images vertically
    # -colorspace sRGB  : prevents a single white/black image from making the whole page black/white
    _convert("-append {images} -colorspace sRGB {output_page_name}".format(
        images=input_image_paths, output_page_name=output_image_path))
    pass


def crop_inplace(crop_sample_range, page_file_path):
    _convert("-crop {sample} {file} {file}".format(sample=crop_sample_range, file=page_file_path))
    pass


def ensure_consistent_width(target_width, images):
    if target_width == 0:
        logger.debug("No given width, extracting first images width: %s " % images[0])
        target_width = images[0].width

    logger.info("Checking input images are target width: " + str(target_width))

    for image in images:
        if image.width != target_width:
            logger.verbose("File {file} not target width {target_width}, current width {current_width}"
                           .format(file=image.path, target_width=target_width, current_width=image.width))
            resize_width(target_width, image.path)
            image.width = target_width

    pass


def ends_in_breakpoint(image, split_on_colour, colour_error_tolerance, colour_standard_deviation):
    file_sample = "{file_name}[{width}x1+0+{height}]".format(file_name=image.path,
                                                             width=image.width-1,
                                                             height=image.height-1)
    gray_mean_value = get_image_gray_mean(file_sample)
    standard_deviation = get_image_standard_deviation(file_sample)

    for colour in split_on_colour:
        colour_difference = int(gray_mean_value) - int(colour)
        if abs(colour_difference) <= colour_error_tolerance \
                and standard_deviation <= colour_standard_deviation:
            logger.debug("Image {file_sample} ends in a breakpoint colour {colour}".format(file_sample=file_sample,
                                                                                           colour=colour))
            return True
        else:
            logger.verbose("Image {file_sample} does not end in a breakpoint colour {colour} (found gray mean value "
                           "{gray_mean} and standard deviation {standard_deviation})"
                           .format(file_sample=file_sample, colour=colour,
                                   gray_mean=gray_mean_value, standard_deviation=standard_deviation))

    return False


def sample_contains_colour(file_sample, split_on_colour, colour_error_tolerance):
    for colour in split_on_colour:
        logger.debug("Checking for colour {colour} using sampling: {file_sample}"
                     .format(colour=colour, file_sample=file_sample))

        gray_min_value = get_image_gray_min(file_sample)
        gray_max_value = get_image_gray_max(file_sample)
        logger.verbose("File colour range: {min}-{max}".format(min=gray_min_value, max=gray_max_value))

        if colour + colour_error_tolerance >= gray_min_value \
                and gray_max_value >= colour - colour_error_tolerance:
            logger.verbose("File sampling contains breakpoint colour within error tolerance")
            return True
        else:
            logger.debug("File sampling did not contain breakpoint colour within error tolerance")

    return False


def find_breakpoint(image, offset, batch_size, row_check_increment,
                    split_on_colour, colour_error_tolerance, colour_standard_deviation):
    logger.debug("Scanning file " + image.path + " for breakpoint with offset " + str(offset))

    batch_end = offset
    while batch_end < image.height - 1:
        logger.inline_progress()
        batch_start = batch_end
        batch_end = min(batch_start + batch_size, image.height - 1)
        batch_file_sample = "{file}[{width}x1+0+{row}]" \
            .format(file=image.path, width=image.width-1, row=batch_start)
        logger.verbose("Checking batch for possible breakpoint colours {colours}: {start}-{end}"
                       .format(colours=split_on_colour, start=batch_start, end=batch_end))

        if not sample_contains_colour(batch_file_sample, split_on_colour, colour_error_tolerance):
            logger.debug("Colours not found in sample batch {start}-{end}, skipping to next batch"
                         .format(start=batch_start, end=batch_end))
            continue
        else:
            logger.verbose("Colours found in sample batch {start}-{end}, checking rows for breakpoint"
                           .format(start=batch_start, end=batch_end))

        for index in range(batch_start, batch_end, row_check_increment):
            file_sampling = "{file}[{width}x1+0+{row}]" \
                .format(file=image.path, width=image.width-1, row=index)
            gray_mean_value = get_image_gray_mean(file_sampling)
            for colour in split_on_colour:
                logger.verbose("Checking row {i} for breakpoint colour {colour}".format(i=index, colour=colour))
                colour_difference = gray_mean_value - colour

                if abs(colour_difference) <= colour_error_tolerance:
                    standard_deviation = get_image_standard_deviation(file_sampling)
                    if standard_deviation <= colour_standard_deviation:
                        logger.debug("Found a breakpoint colour {colour} in {image_name} at row {row}"
                                     .format(colour=colour, image_name=image.path, row=index))
                        return index
                    else:
                        logger.verbose("Colour value {gray_mean} was within tolerance {colour} "
                                       "+-{colour_error} but standard-deviation was {standard_deviation}"
                                       .format(gray_mean=gray_mean_value, colour=colour,
                                               colour_error=colour_error_tolerance, standard_deviation=standard_deviation
                                               ))

    # If we couldn't find a breakpoint, then return 0's
    logger.verbose("Could not find a breakpoint in: " + image.path)
    return -1


