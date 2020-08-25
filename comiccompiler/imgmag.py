import subprocess
import re

from . import logger


# Try to avoid calling command other than imgmag ones in order to prevent cross-os problems
def _command(command):
    # print("Running command: " + command)
    # For whatever reason, close_fds=True causes the program to run reeaaally slowly. Like 2x as slow.
    process = subprocess.Popen(command, shell=True, close_fds=False,
                               stdin=subprocess.PIPE, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    out, err = process.communicate()
    return out.decode('utf-8')


def _identify(params):
    return _command("magick identify " + params)


def _convert(params):
    return _command("magick convert " + params)


def _compare(params):
    return _command("magick compare " + params)


def _ensure_quotes(path):
    if path.startswith('"'):
        return path

    sample_regex = re.search(r"^(.+)([.+])$", path)
    if sample_regex is not None:
        return '"' + sample_regex.group(1) + '"' + sample_regex.group(2)

    return '"' + path + '"'


def get_image_width(image_path):
    return int(_identify('-format "%w" ' + _ensure_quotes(image_path)))


def get_image_height(image_path):
    return int(_identify('-format "%h" ' + _ensure_quotes(image_path)))


def get_image_gray_min(image_path):
    return round(float(_identify('-format %[min] ' + _ensure_quotes(image_path))))


def get_image_gray_mean(image_path):
    return round(float(_identify('-format %[mean] ' + _ensure_quotes(image_path))))


def get_image_gray_max(image_path):
    return round(float(_identify('-format %[max] ' + _ensure_quotes(image_path))))


def get_image_standard_deviation(image_path):
    return round(float(_identify('-format %[standard-deviation] ' + _ensure_quotes(image_path))))


def resize_width(target_width, image_path):
    _convert('{file} -resize {width}x {file}'.format(file=_ensure_quotes(image_path), width=target_width))
    pass


def split(image_path, max_height, file_path_prefix, extension):
    _convert('{file} -crop x{height} {file_path_prefix}-%02d.{extension}'
             .format(file=_ensure_quotes(image_path), height=max_height,
                     file_path_prefix=file_path_prefix, extension=extension))
    return None


def _compare_files(one, two):
    sample_one = _ensure_quotes(one)
    sample_two = _ensure_quotes(two)
    result = _compare('-metric rmse {} {} null: 2>&1'.format(sample_one, sample_two))
    logger.verbose("Compared {} and {} to get result: {}".format(sample_one, sample_two, result))
    return result


def matches(file_one, file_two):
    return _compare_files(file_one, file_two) == "0 (0)"


def almost_matches(file_one, file_two):
    result = _compare_files(file_one, file_two)
    logger.verbose("File sample comparison result: " + result)
    return result == "0 (0)" or " (0.0" in result or " (0.1" in result


def combine_vertically(input_image_paths, output_image_path):
    # -append           : will stitch together the images vertically
    # -colorspace sRGB  : prevents a single white/black image from making the whole page black/white
    logger.debug("Combining images into output file: " + output_image_path)
    _convert('-append {images} -colorspace sRGB {output_page_name}'.format(
        images=" ".join(map(lambda image_path: _ensure_quotes(str(image_path)), input_image_paths)),
        output_page_name=_ensure_quotes(output_image_path))
    )
    pass


def crop_in_place(file, width, height, top_offset):
    crop_sample_range = "{width}x{height}+0+{top_offset}".format(
        width=width, height=height, top_offset=top_offset
    )
    logger.debug("Cropping: {file}[{sample}]".format(file=file, sample=crop_sample_range))
    _convert('-crop {sample} {file} {file}'.format(sample=crop_sample_range, file=_ensure_quotes(file)))
    pass


def sample_is_colour(file_sample, split_on_colour, colour_error_tolerance, colour_standard_deviation):
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


def image_bottom_row_is_colour(image, split_on_colour, colour_error_tolerance, colour_standard_deviation):
    file_sample = get_file_sample_string(image.info["path"], width=image.width, y_offset=image.height-1)
    return sample_is_colour(file_sample, split_on_colour, colour_error_tolerance, colour_standard_deviation)


def _is_row_colour(image, index, split_on_colour, colour_error_tolerance, colour_standard_deviation):
    file_sampling = get_file_sample_string(image.info["path"], width=image.width, y_offset=index)
    gray_mean_value = get_image_gray_mean(file_sampling)
    for colour in split_on_colour:
        logger.verbose("Checking row {i} for breakpoint colour {colour}".format(i=index, colour=colour))
        colour_difference = gray_mean_value - colour

        if abs(colour_difference) <= colour_error_tolerance:
            standard_deviation = get_image_standard_deviation(file_sampling)
            if standard_deviation <= colour_standard_deviation:
                logger.debug("Found a breakpoint colour {colour} in {image_name} at row {row}"
                             .format(colour=colour, image_name=image.info["path"], row=index))
                return True
            else:
                logger.verbose("Colour value {gray_mean} was within tolerance {colour} "
                               "+-{colour_error} but standard-deviation was {standard_deviation}"
                               .format(gray_mean=gray_mean_value, colour=colour,
                                       colour_error=colour_error_tolerance, standard_deviation=standard_deviation
                                       ))
    return False


def find_consecutive_rows_of_colour(image, offset, batch_size, row_check_increment, max_range,
                                    split_on_colour, colour_error_tolerance, colour_standard_deviation):
    logger.debug("Scanning file " + image.info["path"] + " for breakpoint with offset " + str(offset))
    breakpoint_rows = [-1, -1]

    batch_end = offset
    while batch_end < image.height - 1 and breakpoint_rows[1] < 0:
        logger.inline_progress()
        batch_start = batch_end
        batch_end = min(batch_start + batch_size, image.height - 1)
        batch_file_sample = get_file_sample_string(image.info["path"], width=image.width, y_offset=batch_start)
        logger.verbose("Checking batch for possible breakpoint colours {colours}: {start}-{end}"
                       .format(colours=split_on_colour, start=batch_start, end=batch_end))

        if breakpoint_rows[0] < 0:
            if not sample_contains_colour(batch_file_sample, split_on_colour, colour_error_tolerance):
                logger.debug("Colours not found in sample batch {start}-{end}, skipping to next batch"
                             .format(start=batch_start, end=batch_end))
                continue
            else:
                logger.verbose("Colours found in sample batch {start}-{end}, checking rows for breakpoint"
                               .format(start=batch_start, end=batch_end))

        for index in range(batch_start, batch_end, row_check_increment):
            if breakpoint_rows[0] >= 0 and index - breakpoint_rows[0] > max_range:
                breakpoint_rows[1] = breakpoint_rows[0] + max_range
                logger.debug("Reached max range allowed for breakpoint range: " + str(breakpoint_rows[1]))
                return breakpoint_rows

            if _is_row_colour(image, index, split_on_colour, colour_error_tolerance, colour_standard_deviation):
                if breakpoint_rows[0] < 0:
                    breakpoint_rows[0] = index
                    logger.debug("Found first positive breakpoint location: " + str(breakpoint_rows[0]))
            else:
                if breakpoint_rows[0] >= 0:
                    breakpoint_rows[1] = index - row_check_increment
                    logger.debug("Found last positive breakpoint location: " + str(breakpoint_rows[1]))
                    return breakpoint_rows

    if breakpoint_rows[0] >= 0:
        logger.verbose("Found breakpoints all the way to end of file")
        breakpoint_rows[1] = image.height - 1
    else:
        logger.verbose("Could not find a breakpoint in: " + image.info["path"])

    return breakpoint_rows


def get_file_sample_string(path, width=1, height=1, x_offset=0, y_offset=0):
    return '"{path}"[{width}x{height}+{x_offset}+{y_offset}]' \
        .format(path=path, width=width-1, height=height, x_offset=x_offset, y_offset=y_offset)
