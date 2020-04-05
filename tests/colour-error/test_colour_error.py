import unittest
import tests

from comiccompiler import compiler


class ColourErrorTests(tests.ComicomTestCase):
    def test_default(self):
        self.setup_test_vars("colour-error", "Compiled-default")
        self.args.min_height_per_page = 100
        compiler.run(self.args)
        self.compare_output()

    def test_colour_error(self):
        self.setup_test_vars("colour-error", "Compiled-ce10000")
        self.args.min_height_per_page = 100
        self.args.colour_error_tolerance = 10000
        compiler.run(self.args)
        self.compare_output()

    def test_colour_error_too_low(self):
        self.setup_test_vars("colour-error", "Compiled-default")
        self.args.min_height_per_page = 100
        self.args.colour_error_tolerance = 5000
        compiler.run(self.args)
        self.compare_output()


if __name__ == '__main__':
    unittest.main()
