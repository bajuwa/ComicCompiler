import unittest
import tests

from comiccompiler import compiler


class ColourErrorTests(tests.ComicomTestCase):
    def test_colour_error(self):
        self.setup_test_vars("colour-error", "Compiled-ce5000-b1")
        self.args.colour_error_tolerance = 5000
        self.args.breakpoint_detection_mode = 1
        compiler.run(self.args)
        self.compare_output()


if __name__ == '__main__':
    unittest.main()
