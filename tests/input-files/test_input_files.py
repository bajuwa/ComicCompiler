import unittest
import tests

from comiccompiler import compiler


class InputFilesTest(tests.ComicomTestCase):
    def test_aborts_if_no_input(self):
        self.setup_test_vars("input-files", "Compiled-empty")
        self.args.input_files = ["fake"]
        compiler.run(self.args)
        self.compare_output()

    def test_excludes_non_images(self):
        self.setup_test_vars("input-files", "Compiled-exclude-non-images")
        self.args.input_files = [self.base_path + "input/*.*"]
        compiler.run(self.args)
        self.compare_output()


if __name__ == '__main__':
    unittest.main()
