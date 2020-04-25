import glob
import unittest
import os

from comiccompiler import arguments
from comiccompiler import imgmag


# Imports not working? Make sure it's installed by pip, and to install the current dev version:
# pip install --editable <path/to/ComicCompiler/>
# Run tests from base project folder via: python -m unittest
# Cleanup test output folders via: python tests/cleanup.py
class ComicomTestCase(unittest.TestCase):
    def setup_test_vars(self, test_folder, expected_output_folder, actual_output_folder="Compiled"):
        self.expected_output_folder = expected_output_folder
        if actual_output_folder is None:
            self.actual_output_folder = "Compiled"
        else:
            self.actual_output_folder = self.expected_output_folder + "-test"
        self.args = arguments.get_defaults()
        self.base_path = os.path.abspath(os.path.dirname(__file__)) + os.sep + test_folder + os.sep
        self.args.input_files = [self.base_path + "input/*.jpg"]
        self.args.output_directory = self.base_path + self.actual_output_folder + os.sep
        self.args.breakpoint_detection_mode = 0
        self.args.breakpoint_buffer = "0px"
        self.args.clean = True
        # self.args.logging_level = 5

    def compare_output(self):
        expected_files = self.get_expected_files()
        actual_files = self.get_actual_files()

        self.assertEqual(len(actual_files), len(expected_files), "Output file count did not match")
        for i in range(0, len(actual_files)):
            self.assertTrue(imgmag.almost_matches(actual_files[i], expected_files[i]),
                            "Output file content mismatch: " + actual_files[i])

    def get_expected_files(self):
        return glob.glob(self.base_path + self.expected_output_folder + "/*.jpg")

    def get_actual_files(self):
        return glob.glob(self.base_path + self.actual_output_folder + "/*.jpg")
