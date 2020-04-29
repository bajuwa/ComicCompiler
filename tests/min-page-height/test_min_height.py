import unittest
import tests

from comiccompiler import compiler


class MinHeightTests(tests.ComicomTestCase):
    def test_default_args(self):
        self.setup_test_vars("min-page-height", "Compiled-default")
        self.args.min_height_per_page = 400
        compiler.run(self.args)
        self.compare_output()

    def test_breakpoint_unset_default(self):
        self.setup_test_vars("min-page-height", "Compiled-default")
        self.args.min_height_per_page = 400
        self.args.breakpoint_detection_mode = -1
        compiler.run(self.args)
        self.compare_output()

    def test_breakpoint_unset_dynamic(self):
        self.setup_test_vars("min-page-height", "Compiled-b1")
        self.args.min_height_per_page = 300
        self.args.breakpoint_detection_mode = -1
        compiler.run(self.args)
        self.compare_output()

    def test_breakpoint_dynamic(self):
        self.setup_test_vars("min-page-height", "Compiled-b1")
        self.args.min_height_per_page = 300
        self.args.breakpoint_detection_mode = 1
        compiler.run(self.args)
        self.compare_output()


if __name__ == '__main__':
    unittest.main()
