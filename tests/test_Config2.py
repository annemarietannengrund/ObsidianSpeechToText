import unittest
from unittest.mock import patch
from src.Config import Config


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.config = Config()

    def test_get_script_args(self):
        with patch('argparse.ArgumentParser.parse_args') as mocked_parse_args:
            # Prepare mock
            mocked_parse_args.return_value.kwargs = ['key1=value1', 'key2=value2']

            # Call method under test
            result = self.config.get_script_args()

            # Check result
            self.assertDictEqual(result, {'key1': 'value1', 'key2': 'value2'})

    def test_get_language(self):
        with patch.dict('os.environ', {'OSTTC_LANGUAGE': 'fr'}):
            # Call method under test
            result = self.config.get_language()

            # Check result
            self.assertEqual(result, 'fr')

    def test_get_model_size(self):
        with patch.dict('os.environ', {'OSTTC_MODEL_SIZE': 'large'}):
            # Call method under test
            result = self.config.get_model_size()

            # Check result
            self.assertEqual(result, 'large')

    def test_get_path(self):
        with patch.dict('os.environ', {'OSTTC_LOCAL_PATH': './new_folder'}):
            # Call method under test
            result = self.config.get_path()

            # Check result
            self.assertEqual(result, './new_folder')

    def test_get_action_keywords(self):
        with patch.dict('os.environ', {'OSTTC_KEYWORDS': '1'}):
            # Call method under test
            result = self.config.get_action_keywords()

            # Check result
            self.assertDictEqual(result, self.config.ACTION_KEYWORDS)

    def test_get_overwrite_existing(self):
        with patch.dict('os.environ', {'OSTTC_OVERWRITE': '1'}):
            # Call method under test
            result = self.config.get_overwrite_existing()

            # Check result
            self.assertEqual(result, 1)

    def test_get_source_string_format(self):
        with patch.dict('os.environ', {'OSTTC_SOURCE_STRING': 'NewFormat'}):
            # Call method under test
            result = self.config.get_source_string_format()

            # Check result
            self.assertEqual(result, 'NewFormat')

    def test_get_target_string_format(self):
        with patch.dict('os.environ', {'OSTTC_TARGET_STRING': 'NewFormat'}):
            # Call method under test
            result = self.config.get_target_string_format()

            # Check result
            self.assertEqual(result, 'NewFormat')

    def test_get_media_files(self):
        with patch.dict('os.environ', {'OSTTC_MEDIA_FILES': '.flac,.ogg'}):
            # Call method under test
            result = self.config.get_media_files()

            # Check result
            self.assertListEqual(result, ['.flac', '.ogg'])

    def test_get_converter(self):
        # Call method under test
        result = self.config.get_converter()

        # Check result
        self.assertIsNotNone(result)
        self.assertEqual(result.language, self.config.language)
        self.assertEqual(result.model, self.config.model_size)
        self.assertDictEqual(result.actions, self.config.action_keywords)


if __name__ == '__main__':
    unittest.main()
