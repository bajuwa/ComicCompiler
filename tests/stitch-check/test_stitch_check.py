import unittest
import tests

from comiccompiler import compiler


class StitchCheckTests(tests.ComicomTestCase):
    def test_default_args(self):
        self.setup_test_vars("stitch-check", "Compiled-default")
        self.args.enable_stitch_check = True
        compiler.run(self.args)
        self.compare_output()

    def test_similar_connections(self):
        self.setup_test_vars("stitch-check", "Compiled-no-result")
        self.args.enable_stitch_check = True
        self.args.input_files = [self.base_path + "input/image000.jpg", self.base_path + "input/image002.jpg"]
        compiler.run(self.args)
        self.compare_output()

    def test_different_connections(self):
        self.setup_test_vars("stitch-check", "Compiled-no-result")
        self.args.enable_stitch_check = True
        self.args.input_files = [self.base_path + "input/image000.jpg", self.base_path + "input/image000.jpg"]
        compiler.run(self.args)
        self.compare_output()

    def test_similar_connections_disabled(self):
        self.setup_test_vars("stitch-check", "Compiled-disabled-similar")
        self.args.input_files = [self.base_path + "input/image000.jpg", self.base_path + "input/image002.jpg"]
        compiler.run(self.args)
        self.compare_output()

    def test_different_connections_disabled(self):
        self.setup_test_vars("stitch-check", "Compiled-disabled-different")
        self.args.input_files = [self.base_path + "input/image000.jpg", self.base_path + "input/image000.jpg"]
        compiler.run(self.args)
        self.compare_output()


if __name__ == '__main__':
    unittest.main()
