import os
import unittest
from unittest.mock import MagicMock
from datetime import datetime
from src.Converter import ObsidianSpeechToTextConverter
from unittest.mock import Mock, patch


class TestObsidianSpeechToTextConverter(unittest.TestCase):
    class ConfigMock:
        def __init__(self):
            self.path = "input_folder"
            self.overwrite_existing = False
            self.media_files = [".mp3", ".wav"]
            self.source_string = "%Y%m%d_%H%M%S"
            self.target_string = "%Y%m%d"
            self.converter = MagicMock(name="AudioTextProcessor")

    def setUp(self):
        self.converter = ObsidianSpeechToTextConverter(self.ConfigMock())

    def tearDown(self):
        pass

    def test_get_markdown_file_name(self):
        filename = self.converter.get_markdown_file_name("20230303_120000", "some_root")
        self.assertEqual(filename, "some_root/20230303.md")

    def test_get_markdown_file_name_with_invalid_filename_format(self):
        with self.assertLogs() as cm:
            filename = self.converter.get_markdown_file_name("invalid_format", "some_root")
            self.assertEqual(filename, "some_root/invalid_format.md")
            self.assertIn("WARNING:root:The provided source filename 'invalid_format' can't be parsed with",
                          cm.output[0])

    def test_convert_file_in_mime_types(self):
        self.converter.transcribe = MagicMock()
        self.converter.create_transcription_file = MagicMock()
        self.converter.input_folder = "."
        self.converter.media_files = [".txt"]
        with self.assertLogs() as cm:
            self.converter.convert()
            print(cm.output[0])
            self.assertIn("INFO:root:Transcribing:", cm.output[0])

    def test_skip_file_not_in_mime_types(self):
        self.converter.transcribe = MagicMock()
        self.converter.create_transcription_file = MagicMock()
        self.converter.input_folder = "."
        self.converter.media_files = [".mp3"]
        with self.assertLogs() as cm:
            self.converter.convert()
            self.assertIn("INFO:root:Skipping:", cm.output[0])

    def test_transcribe(self):
        self.converter.active_model.transcribe = MagicMock(return_value="sample transcription")
        result = self.converter.transcribe("test.mp3")
        self.assertEqual(result, "sample transcription")

    def test_create_transcription_file(self):
        self.converter.create_transcription_file("test.txt", "Test")
        with open("test.txt", 'r') as f:
            content = f.read()
        self.assertEqual(content, "Test")
        os.remove("test.txt")


if __name__ == '__main__':
    unittest.main()
