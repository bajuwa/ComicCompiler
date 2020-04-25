import unittest
import tests

from comiccompiler import compiler


class BreakpointBufferTests(tests.ComicomTestCase):
    def test_none(self):
        self.setup_test_vars("breakpoint-buffer", "Compiled-bb0")
        self.args.min_height_per_page = 100
        self.args.breakpoint_detection_mode = 1
        self.args.breakpoint_buffer = "0px"
        compiler.run(self.args)
        self.compare_output()

    def test_pixel(self):
        self.setup_test_vars("breakpoint-buffer", "Compiled-bb20")
        self.args.min_height_per_page = 100
        self.args.breakpoint_detection_mode = 1
        self.args.breakpoint_buffer = "20px"
        compiler.run(self.args)
        self.compare_output()

    def test_percent(self):
        self.setup_test_vars("breakpoint-buffer", "Compiled-bb-half")
        self.args.min_height_per_page = 100
        self.args.breakpoint_detection_mode = 1
        self.args.breakpoint_buffer = "50%"
        compiler.run(self.args)
        self.compare_output()


if __name__ == '__main__':
    unittest.main()
