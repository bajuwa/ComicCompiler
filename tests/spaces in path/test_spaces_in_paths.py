import unittest
import tests

from comiccompiler import compiler


class SpacePathTests(tests.ComicomTestCase):
    def test_default(self):
        self.setup_test_vars("spaces in path", "Compiled-default")
        compiler.run(self.args)
        self.compare_output()


if __name__ == '__main__':
    unittest.main()
