from src.AudioTextProcessor import AudioTextProcessor
from time import time
from whisper import load_model
from logging import info, error
from os.path import basename

class AudioTextProcessorWhisper(AudioTextProcessor):
    model_sizes = ["tiny.en", "tiny", "base.en", "base", "small.en", "small", "medium.en", "medium", "large"]

    def __init__(self, language, model, **kwargs):
        self.language = language
        if model not in self.model_sizes:
            raise ValueError(f"Invalid model size. Valid options are: {', '.join(self.model_sizes)}")
        self.model = model
        self.active_model = None
        self.actions = kwargs.get("action_keywords") if kwargs.get("action_keywords", {}) else {}

    def transcribe(self, audio_file: str) -> str:
        if self.active_model is None:
            self.init_model()
        try:
            info("Converting audio transcripts into text ...")
            start = time()
            result = self.active_model.transcribe(audio_file, fp16=False, language=self.language)
            duration = int(time() - start)
            info("end transscription")
            result = result['text'].strip()
            word_count = self.word_counter(result)
            info(f"transcribed {word_count} words in {duration} seconds")
            result = super().format_text(result, self.actions, basename(audio_file))
        except Exception as e:
            error(e)
            raise Exception(f"Error while converting {audio_file} with message: {e}")
        return result

    def init_model(self) -> None:
        info(f"Loading local *{self.model}* whisper model with language code *{self.language}*")
        try:
            self.active_model = load_model(self.model)
        except Exception as e:
            error(e)
        info("Loading of whisper model finished")
