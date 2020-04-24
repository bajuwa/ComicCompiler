from PIL import Image


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
            return self.images[0].info["batch_index"]
        return None

    def get_last_image_index(self):
        if self.image_count() > 0:
            return self.images[self.image_count()-1].info["batch_index"]
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
