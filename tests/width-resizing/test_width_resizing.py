import unittest
import tests

from comiccompiler import compiler


class InputSortingTest(tests.ComicomTestCase):
    def test_default_args(self):
        self.setup_test_vars("width-resizing", "Compiled-default")
        compiler.run(self.args)
        self.compare_output()

    def test_multiple_inputs_with_sorting(self):
        self.setup_test_vars("width-resizing", "Compiled-300px")
        self.args.output_file_width = 300
        compiler.run(self.args)
        self.compare_output()


if __name__ == '__main__':
    unittest.main()
