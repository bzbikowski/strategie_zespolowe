import json
import os
import unittest


class TestConfigFile(unittest.TestCase):
    def setUp(self):
        abs_path = os.path.abspath(os.path.dirname(__file__))
        parent_path = os.path.normpath(os.path.join(abs_path, os.pardir))
        self.path = os.path.join(parent_path, "config.json")

    def test_if_file_exists(self):
        self.assertTrue(os.path.exists(self.path))

    def test_if_format_is_correct(self):
        json_file = None
        try:
            with open(self.path, "r") as f:
                json_file = json.load(f)
        except FileNotFoundError as e:
            self.fail("File 'config.json' not found. ")
        self.assertIn("maps", json_file.keys())
        self.assertIsInstance(json_file["maps"], list)
        for algorithm in json_file["maps"]:
            keywords = ["algorithm", "schema", "help"]
            for key in keywords:
                self.assertIn(key, algorithm.keys())
                data = algorithm[key]
                self.assertIsInstance(data, str)

    def test_if_files_under_map_exists(self):
        # todo complete later
        pass
