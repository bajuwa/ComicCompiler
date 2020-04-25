import unittest
import tests

from comiccompiler import compiler


class BreakpointModeTests(tests.ComicomTestCase):
    def test_default_mode(self):
        self.setup_test_vars("breakpoint-detection-mode", "Compiled-b0")
        self.args.min_height_per_page = 100
        self.args.breakpoint_detection_mode = 0
        compiler.run(self.args)
        self.compare_output()

    def test_dynamic_search_mode(self):
        self.setup_test_vars("breakpoint-detection-mode", "Compiled-b1")
        self.args.min_height_per_page = 100
        self.args.breakpoint_detection_mode = 1
        compiler.run(self.args)
        self.compare_output()

    def test_unset_too_short(self):
        self.setup_test_vars("breakpoint-detection-mode", "Compiled-b1")
        self.args.min_height_per_page = 100
        self.args.breakpoint_detection_mode = -1
        compiler.run(self.args)
        self.compare_output()


if __name__ == '__main__':
    unittest.main()
