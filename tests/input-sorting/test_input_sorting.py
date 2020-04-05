import unittest
import tests

from comiccompiler import compiler


class InputSortingTest(tests.ComicomTestCase):
    def test_default_args(self):
        self.setup_test_vars("input-sorting", "Compiled-default")
        compiler.run(self.args)
        self.compare_output()

    def test_multiple_inputs_with_sorting(self):
        self.setup_test_vars("input-sorting", "Compiled-sorted")
        self.args.input_files = [self.base_path + "input/image[0-9][0-9].jpg", self.base_path + "input/image[0-9].jpg"]
        compiler.run(self.args)
        self.compare_output()

    def test_multiple_inputs_without_sorting(self):
        self.setup_test_vars("input-sorting", "Compiled-unsorted")
        self.args.input_files = [self.base_path + "input/image[0-9][0-9].jpg", self.base_path + "input/image[0-9].jpg"]
        self.args.disable_input_sort = True
        compiler.run(self.args)
        self.compare_output()


if __name__ == '__main__':
    unittest.main()
