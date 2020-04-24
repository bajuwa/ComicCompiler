import unittest
import tests

from comiccompiler import compiler


class MinHeightLastPageTest(tests.ComicomTestCase):
    def test_default_args(self):
        self.setup_test_vars("min-last-page-height", "Compiled-default")
        self.args.min_height_per_page = 400
        self.args.min_height_last_page = 10
        compiler.run(self.args)
        self.compare_output()

    def test_pixel(self):
        self.setup_test_vars("min-last-page-height", "Compiled-adopt-orphan")
        self.args.min_height_per_page = 400
        self.args.min_height_last_page = "400px"
        compiler.run(self.args)
        self.compare_output()

    def test_format(self):
        self.setup_test_vars("min-last-page-height", "Compiled-adopt-orphan")
        self.args.min_height_per_page = "30%"
        self.args.min_height_last_page = "50%"
        compiler.run(self.args)
        self.compare_output()

    def test_breakpoint(self):
        self.setup_test_vars("min-last-page-height", "Compiled-adopt-orphan-b1")
        self.args.min_height_per_page = 400
        self.args.min_height_last_page = 400
        self.args.breakpoint_detection_mode = 1
        compiler.run(self.args)
        self.compare_output()


if __name__ == '__main__':
    unittest.main()
