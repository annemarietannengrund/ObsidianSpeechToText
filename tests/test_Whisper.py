import unittest
from unittest.mock import patch, Mock
from src.processor.Whisper import Whisper


class TestWhisper(unittest.TestCase):

    @patch('src.processor.Whisper.load_model', return_value='mocked_model')
    def setUp(self, load_model_mock):
        self.whisper = Whisper('en', 'tiny')
        self.assertEqual(load_model_mock.call_count, 0)

    @patch('src.processor.Whisper.info', side_effect=print)
    @patch('src.processor.Whisper.time', return_value=0)
    @patch('src.processor.Whisper.load_model', return_value='mocked_model')
    def test_transcribe(self, load_model_mock, time_mock, info_mock):
        audio_file = 'test.mp3'
        result_text = 'Test text'
        mocked_model = Mock()
        mocked_model.transcribe.return_value = {'text': result_text}
        load_model_mock.return_value = mocked_model
        self.whisper.active_model = mocked_model
        transcribed_text = self.whisper.transcribe(audio_file)
        mocked_model.transcribe.assert_called_once_with(audio_file, fp16=False, language='en')
        self.assertEqual(transcribed_text.strip(), result_text)

    @patch('src.processor.Whisper.load_model', side_effect=Exception('Error occurred while loading model'))
    @patch('src.processor.Whisper.error', side_effect=print)
    def test_transcribe_exception(self, error_mock, load_model_mock):
        audio_file = 'test.mp3'
        self.whisper.active_model = None
        with self.assertRaises(Exception) as context:
            self.whisper.transcribe(audio_file)
        self.assertTrue('Error while converting' in str(context.exception))

    @patch('src.processor.Whisper.info', side_effect=print)
    @patch('src.processor.Whisper.load_model', return_value='mocked_model')
    def test_init_model(self, load_model_mock, info_mock):
        self.whisper.active_model = None
        self.whisper.init_model()
        load_model_mock.assert_called_once_with('tiny')
        self.assertEqual(self.whisper.active_model, 'mocked_model')


if __name__ == "__main__":
    unittest.main()
