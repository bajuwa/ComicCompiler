import unittest
import tests

from comiccompiler import compiler


class SpecialCharactersTest(tests.ComicomTestCase):
    def test_default(self):
        self.setup_test_vars("中文 and 😊", "Compiled-default")
        compiler.run(self.args)
        self.compare_output()


if __name__ == '__main__':
    unittest.main()
