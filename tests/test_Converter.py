import unittest
from unittest.mock import Mock, patch
from src.Converter import ObsidianSpeechToTextConverter


class TestObsidianSpeechToTextConverter(unittest.TestCase):
    def setUp(self):
        self.mock_config = Mock()
        self.mock_config.path = "/test/path"
        self.mock_config.overwrite_existing = False
        self.mock_config.media_files = [".wav", ".mp3"]
        self.mock_config.source_string = "%Y_%m_%d_%H_%M_%S"
        self.mock_config.target_string = "%Y-%m-%d-%H-%M-%S"
        self.mock_config.converter = Mock()

        self.converter = ObsidianSpeechToTextConverter(self.mock_config)

        self.root_path = "/some/path"
        self.source_filename = "test_file"

    def test_get_markdown_file_name(self):
        final_name = self.converter.get_markdown_file_name(self.source_filename, self.root_path)
        expected_name = f"{self.root_path}/test_file.md"
        self.assertEqual(final_name, expected_name)

    def test_convert_exception(self):
        self.converter.active_model = None
        with self.assertRaises(Exception):
            self.converter.convert()

    def test_transcribe(self):
        test_audio_file = "test_audio_file"
        self.mock_config.converter.transcribe.return_value = "transcription"
        transcription = self.converter.transcribe(test_audio_file)
        self.assertEqual(transcription, "transcription")
        self.mock_config.converter.transcribe.assert_called_once_with(test_audio_file)

    @patch("src.Converter.open", create=True)
    def test_create_transcription_file(self, mock_open):
        test_file = "test_file"
        test_content = "test_content"
        self.converter.create_transcription_file(test_file, test_content)
        mock_open.assert_called_once_with(test_file, "w")
        mock_open().__enter__().write.assert_called_once_with(test_content)


if __name__ == '__main__':
    unittest.main()
