import unittest
import tests

from comiccompiler import compiler


class MinHeightFormatTests(tests.ComicomTestCase):
    def test_pixel_legacy(self):
        self.setup_test_vars("min-page-height-formats", "Compiled-pixel")
        self.args.min_height_per_page = "300"
        compiler.run(self.args)
        self.compare_output()

    def test_pixel(self):
        self.setup_test_vars("min-page-height-formats", "Compiled-pixel")
        self.args.min_height_per_page = "300px"
        compiler.run(self.args)
        self.compare_output()

    def test_ratio(self):
        self.setup_test_vars("min-page-height-formats", "Compiled-ratio")
        self.args.min_height_per_page = "1:2"
        compiler.run(self.args)
        self.compare_output()

    def test_fraction(self):
        self.setup_test_vars("min-page-height-formats", "Compiled-fraction")
        self.args.min_height_per_page = "1/2"
        compiler.run(self.args)
        self.compare_output()

    def test_percent(self):
        self.setup_test_vars("min-page-height-formats", "Compiled-percent")
        self.args.min_height_per_page = "30%"
        compiler.run(self.args)
        self.compare_output()


if __name__ == '__main__':
    unittest.main()
