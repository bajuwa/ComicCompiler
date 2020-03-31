
class Arguments:
    logging_level = 1
    input_directory = "./"
    input_file_prefix = "image"
    extension = ".jpg"
    output_file_width = 0
    output_directory = "./Compiled/"
    clean = False
    open = False
    exit = False
    split_on_colour = [0, 65535]
    colour_error_tolerance = 0
    colour_standard_deviation = 0
    break_points_increment = 10
    break_points_multiplier = 20
    min_height_per_page = 5000
    breakpoint_detection_mode = 0
    output_file_prefix = "page"
    output_file_starting_number = 1

    def __str__(self):
        return "Arguments{" \
                "logging_level = " + str(self.logging_level) + \
                ", input_directory = " + str(self.input_directory) + \
                ", input_file_prefix = " + str(self.input_file_prefix) + \
                ", extension = " + str(self.extension) + \
                ", output_file_width = " + str(self.output_file_width) + \
                ", output_directory = " + str(self.output_directory) + \
                ", split_on_colour = " + str(self.split_on_colour) + \
                ", colour_error_tolerance = " + str(self.colour_error_tolerance) + \
                ", colour_standard_deviation = " + str(self.colour_standard_deviation) + \
                ", breakpoint_detection_mode = " + str(self.breakpoint_detection_mode) + \
                ", break_points_increment = " + str(self.break_points_increment) + \
                ", break_points_multiplier = " + str(self.break_points_multiplier) + \
                ", min_height_per_page = " + str(self.min_height_per_page) + \
                ", output_file_prefix = " + str(self.output_file_prefix) + \
                ", output_file_starting_number = " + str(self.output_file_starting_number) + \
                ", clean = " + str(self.clean) + \
                ", open = " + str(self.open) + \
                ", exit = " + str(self.exit) + \
               "}"


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
