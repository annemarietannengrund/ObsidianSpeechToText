import unittest

from src.abstracts.AudioTextProcessor import AudioTextProcessor


class MockAudioTextProcessor(AudioTextProcessor):
    def init_model(self):
        return "Model Initialized"

    def transcribe(self, audio_file):
        return "Transcribed Text"


class TestAudioTextProcessor(unittest.TestCase):

    def setUp(self):
        self.audio_processor = MockAudioTextProcessor()

    def test_transcribe(self):
        # abstract method, not implemented in this class
        pass

    def test_init_model(self):
        # abstract method, not implemented in this class
        pass

    def test_format_text(self):
        text = "AudioTextProcessor"
        words = {"Audio": "Audio_"}
        audio_file_name = "audio_file"
        result = self.audio_processor.format_text(text, words, audio_file_name)
        self.assertEqual(result, "Audio_TextProcessor")

        text = "AudioTextProcessor"
        words = {}
        audio_file_name = "audio_file"
        result = self.audio_processor.format_text(text, words, audio_file_name)
        self.assertEqual(result, text)

    def test_create_properties_header(self):
        # tags and audio
        properties = ["tags", "audio log"]
        link_audio = "link_audio"
        expectation = '---\ntags\naudio log\n---\n![[link_audio]]\n'
        result = self.audio_processor.create_properties_header(properties, link_audio)
        self.assertEqual(result, expectation)

        # tags but no audio
        properties = ["tags", ""]
        link_audio = ""
        expectation = '---\ntags\n\n---\n'
        result = self.audio_processor.create_properties_header(properties, link_audio)
        self.assertEqual(result, expectation)

        # no tags and no audio
        properties = ["", ""]
        link_audio = "link_audio"
        expectation = '![[link_audio]]\n'
        result = self.audio_processor.create_properties_header(properties, link_audio)
        self.assertEqual(result, expectation)

    def test_get_tags_str_for_properties(self):
        text = "test text"
        result = self.audio_processor.get_tags_str_for_properties(text)
        self.assertEqual(result, "")

        text = "test #TAGS--- Alpha Beta, Ceta Eta. Feta, ---TAGS# text"
        expectation = "tags:\n  - Alpha\n  - Beta\n  - Ceta\n  - Eta\n  - Feta"
        result = self.audio_processor.get_tags_str_for_properties(text)
        self.assertEqual(result, expectation)

    def test_get_audiofile_keyword_for_properties(self):
        audio_file_name = "audio_file"
        result = self.audio_processor.get_audiofile_keyword_for_properties(audio_file_name)
        self.assertEqual(result, 'audiolog: "[[audio_file]]"')

        audio_file_name = ""
        result = self.audio_processor.get_audiofile_keyword_for_properties(audio_file_name)
        self.assertEqual(result, '')

    def test_has_audiofile_keyword(self):
        text = "test text"
        audio_file_name = "audio_file"
        result = self.audio_processor.has_audiofile_keyword(text, audio_file_name)
        self.assertEqual(result, "")

    def test_remove_obsidian_tags_from_text(self):
        text = "test #TAGS---text---TAGS#text"
        result = self.audio_processor.remove_obsidian_tags_from_text(text)
        self.assertEqual("test text", result)

    def test_remove_audiofile_keyword(self):
        text = "test #LINK_AUDIO_FILE#text"
        result = self.audio_processor.remove_audiofile_keyword(text)
        self.assertEqual("test text", result)

    def test_format_hashtags(self):
        text = "I love my cat Hashtag kitten, Hashtag live laugh love. Hashtag so cute. now to something different"
        result = self.audio_processor.format_hashtags(text)
        self.assertEqual(result, "I love my cat #Kitten #LiveLaughLove #SoCute now to something different")

    def test_word_counter(self):
        text = "Testing word counter."
        result = self.audio_processor.word_counter(text)
        self.assertEqual(result, 3)


if __name__ == '__main__':
    unittest.main()
