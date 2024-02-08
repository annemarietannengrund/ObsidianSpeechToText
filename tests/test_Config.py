import unittest

from src.Config import Config
from unittest.mock import patch


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.config = Config()

    @patch('Config.getenv', return_value='en')
    def test_get_language(self, mock_getenv):
        self.assertEqual(self.config.get_language(), 'en')
        mock_getenv.assert_called_once_with('OSTTC_LANGUAGE', default=self.config.DEFAULT_LANGUAGE)

    @patch('Config.getenv', return_value='large')
    def test_get_model_size(self, mock_getenv):
        self.assertEqual(self.config.get_model_size(), 'large')
        mock_getenv.assert_called_once_with('OSTTC_MODEL_SIZE', default=self.config.DEFAULT_MODEL_SIZ)

    @patch('Config.getenv', return_value='./new_path')
    def test_get_path(self, mock_getenv):
        self.assertEqual(self.config.get_path(), './new_path')
        mock_getenv.assert_called_once_with('OSTTC_LOCAL_PATH', default=self.config.DEFAULT_LOCAL_PATH)

    @patch('Config.getenv', return_value='0')
    def test_get_action_keywords(self, mock_getenv):
        self.assertEqual(self.config.get_action_keywords(), {})
        mock_getenv.assert_called_once_with('OSTTC_KEYWORDS', default=self.config.DEFAULT_USE_KEYWORDS)

    @patch('Config.getenv', return_value='1')
    def test_get_overwrite_existing(self, mock_getenv):
        self.assertEqual(self.config.get_overwrite_existing(), 1)
        mock_getenv.assert_called_once_with('OSTTC_OVERWRITE', default=self.config.DEFAULT_OVERWRITE)

    @patch('Config.getenv', return_value='new_format')
    def test_get_source_string_format(self, mock_getenv):
        self.assertEqual(self.config.get_source_string_format(), 'new_format')
        mock_getenv.assert_called_once_with('OSTTC_SOURCE_STRING', default=self.config.SOURCE_STRING_FORMAT)

    @patch('Config.getenv', return_value='new_format')
    def test_get_target_string_format(self, mock_getenv):
        self.assertEqual(self.config.get_target_string_format(), 'new_format')
        mock_getenv.assert_called_once_with('OSTTC_TARGET_STRING', default=self.config.TARGET_STRING_FORMAT)

    @patch('Config.getenv', return_value='.ogg,.mp4')
    def test_get_media_files(self, mock_getenv):
        self.assertEqual(self.config.get_media_files(), ['.ogg', '.mp4'])
        mock_getenv.assert_called_once_with('OSTTC_MEDIA_FILES', default=self.config.MEDIA_FILES)

    @patch('Config.Whisper')
    def test_get_converter(self, mock_whisper):
        mock_whisper_instance = mock_whisper.return_value
        self.assertEqual(self.config.get_converter(), mock_whisper_instance)

    def test_init(self):
        with patch.object(Config, 'get_script_args', return_value={}) as mock_get_script_args, \
                patch.object(Config, 'get_language', return_value='en') as mock_get_language, \
                patch.object(Config, 'get_model_size', return_value='large') as mock_get_model_size, \
                patch.object(Config, 'get_path', return_value='./new_path') as mock_get_path, \
                patch.object(Config, 'get_action_keywords', return_value={}) as mock_get_action_keywords, \
                patch.object(Config, 'get_overwrite_existing', return_value=1) as mock_get_overwrite_existing, \
                patch.object(Config, 'get_source_string_format',
                             return_value='new_format') as mock_get_source_string_format, \
                patch.object(Config, 'get_target_string_format',
                             return_value='new_format') as mock_get_target_string_format, \
                patch.object(Config, 'get_media_files', return_value=[]) as mock_get_media_files, \
                patch.object(Config, 'get_converter') as mock_get_converter:
            Config()
            self.assertTrue(mock_get_script_args.called)
            self.assertTrue(mock_get_language.called)
            self.assertTrue(mock_get_model_size.called)
            self.assertTrue(mock_get_path.called)
            self.assertTrue(mock_get_action_keywords.called)
            self.assertTrue(mock_get_overwrite_existing.called)
            self.assertTrue(mock_get_source_string_format.called)
            self.assertTrue(mock_get_target_string_format.called)
            self.assertTrue(mock_get_media_files.called)
            self.assertTrue(mock_get_converter.called)


if __name__ == "__main__":
    unittest.main()
