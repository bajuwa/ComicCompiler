import unittest
import tests

from comiccompiler import compiler


class ColourStandardDeviationTests(tests.ComicomTestCase):
    def test_default(self):
        self.setup_test_vars("colour-standard-deviation", "Compiled-default")
        self.args.min_height_per_page = 100
        self.args.colour_error_tolerance = 5000
        compiler.run(self.args)
        self.compare_output()

    def test_colour_standard_deviation(self):
        self.setup_test_vars("colour-standard-deviation", "Compiled-csd2000")
        self.args.min_height_per_page = 100
        self.args.colour_error_tolerance = 5000
        self.args.colour_standard_deviation = 2000
        compiler.run(self.args)
        self.compare_output()

    def test_colour_standard_deviation_too_small(self):
        self.setup_test_vars("colour-standard-deviation", "Compiled-default")
        self.args.min_height_per_page = 100
        self.args.colour_error_tolerance = 5000
        self.args.colour_standard_deviation = 200
        compiler.run(self.args)
        self.compare_output()


if __name__ == '__main__':
    unittest.main()
