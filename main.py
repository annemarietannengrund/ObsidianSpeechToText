from abc import ABC, abstractmethod
from argparse import ArgumentParser
from datetime import datetime
from logging import basicConfig, info, error, INFO
from os import remove, walk, getenv
from os.path import join, splitext, basename, exists
from re import sub, IGNORECASE
from time import time

from moviepy.editor import AudioFileClip
from speech_recognition import AudioFile, Recognizer
from whisper import load_model
from dotenv import load_dotenv
load_dotenv()
basicConfig(level=INFO)


class GetTextFromAudio(ABC):
    @abstractmethod
    def transcribe(self, audio_file: str):
        pass

    @abstractmethod
    def init_model(self) -> None:
        pass

    def format_text(self, text, words) -> str:
        if not words:
            return text
        for word, format in words.items():
            text = sub(word, format, text, flags=IGNORECASE)
        return text

    @staticmethod
    def word_counter(text) -> int:
        return len(text.split())


class GetTextFromAudioWhisper(GetTextFromAudio):
    model_sizes = ["tiny.en", "tiny", "base.en", "base", "small.en", "small", "medium.en", "medium", "large"]

    def __init__(self, language, model, **kwargs):
        self.language = language
        if model not in self.model_sizes:
            raise ValueError(f"Invalid model size. Valid options are: {', '.join(self.model_sizes)}")
        self.model = model
        self.active_model = None
        self.format_words = kwargs.get("action_keywords") if kwargs.get("action_keywords", {}) else {}

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
            info(f"transcribed {word_count} in {duration} seconds")
            result = super().format_text(result, self.format_words)
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


class GetTextFromAudioGoogle(GetTextFromAudio):

    def __init__(self, language, **kwargs):
        self.language = language
        self.active_model = None
        self.format_words = kwargs.get("format_words") if kwargs.get("format_words", {}) else {}

    def transcribe(self, audio_file) -> str:
        if self.active_model == None:
            self.init_model()
        tmp_file = audio_file
        if audio_file.endswith(".webm"):
            info("Obsidian audio webm detected, converting to supported wav file format")
            tmp_file = tmp_file.replace(".webm", ".wav")
            clip = AudioFileClip(audio_file)
            clip.write_audiofile(tmp_file)

        with AudioFile(tmp_file) as source:
            audio_text = self.active_model.listen(source)
            info("Converting audio transcripts into text ...")
            try:
                start = time()
                result = self.active_model.recognize_google(audio_text, language=self.language).strip()
                duration = time() - start
                info("end transscription")
                word_count = self.word_counter(result)
                info(f"transcribed {word_count} in {duration} seconds")
            except Exception as e:
                error(e)
                raise Exception(f"Error while converting {audio_file} with message: {e}")

        if audio_file.endswith(".webm"):
            info("removing temporary Obsidian audio wav")
            remove(tmp_file)
        result = super().format_text(result, self.format_words)
        return result

    def init_model(self):
        info(f"Loading online google model with language code *{self.language}*")
        self.active_model = Recognizer()
        info("Loading of google model finished")


class Config:
    # default script configs
    DEFAULT_LANGUAGE = "de"
    DEFAULT_MODEL_SIZ = "medium"
    DEFAULT_LOCAL_PATH = "./recordings"
    DEFAULT_USE_KEYWORDS = 1
    DEFAULT_USE_OFFLINE = 1
    DEFAULT_OVERWRITE = 0
    MEDIA_FILES = ",".join(['.webm', '.mp3', '.wav', '.m4a'])
    """
    Default case for obsidian audio logs, their name in the process is in the format of `Recording 20240205220851`
    in step 1. the SOURCE_STRING_FORMAT will be applied to the remaining file name in the correct format.
    in step 2. the markdown file name created from the audio will be formatted in the TARGET_STRING_FORMAT format
    """
    SOURCE_STRING_FORMAT = "Recording %Y%m%d%H%M%S"
    TARGET_STRING_FORMAT = "%Y-%m-%d-%H-%M.md"
    """
    Based on the model you are using, these regexes rely purely on the formatting of it.
    the models may or may not add commas, points, dashes or other variations of what you have said.

    this said, maybe adding the mistakes the AI makes as expected values instead.
    this is all very experimental and will not always work is intended or expected

    all regexes are processed with an case incentive flag (flags=IGNORECASE).

    best is to copy the text part that did not convert and paste it into https://regex101.com/
    then use the failed regex to figure out one that matches our text.

    regex crashcourse:
    - stuff in [] means one of these
    - a prepended + means many of these
    - a prepended ? means the previous [] or () is optional
    - pipes | are used to make or statements
    - stuff in () requires exact sequence of characters
    """
    ACTION_KEYWORDS = {
        # pairwise instructions
        r"obsidian[-\s]?link (start|anfang)[\s.,]?\s?": "[[",
        r"[.,]?\sobsidian[-\s]?Link (stop|ende)[.,]?\s?": "]]",

        r"obsidian[-,\s]+?(text|tech)[s]?[,]? (start|anfang)[\s.,]?\s?": "#TAGS--- ",
        r"[.,]?\sobsidian[-,\s]+?(text|tech)[,\s]? (stop|ende)[.,]?\s?": " ---TAGS#",

        # single line instructions
        r"(Line Break|Absatz|Zeilenumbruch)[.,]?\s?": "\n",
        r"\s?(Zitat (Anfang|Start|start))[.,]?\s?": "\n> ",
        r"Überschrift H1[.,]?\s?": "# ",
        r"Überschrift H2[.,]?\s?": "## ",
        r"Überschrift H3[.,]?\s?": "### ",
        r"Überschrift H4[.,]?\s?": "#### ",
        r"Überschrift H5[.,]?\s?": "##### ",
        r"Überschrift H6[.,]?\s?": "###### ",
        r"Gedankenstrich": "—",
        r"\s?Listenstrich[\s.,]?": "\n- ",
    }

    def __init__(self) -> None:
        self.script_args = self.get_script_args()
        self.use_docker = int(getenv("RUNS_ON_DOCKER", default="0"))
        self.language = self.get_language()
        self.model_size = self.get_model_size()
        self.path = self.get_path()
        info(f"input_folder has been configured to '{self.path}'")
        self.action_keywords = self.get_action_keywords()
        self.use_offline = self.get_use_offline()
        self.overwrite_existing = self.get_overwrite_existing()
        self.source_string = self.get_source_string_format()
        self.target_string = self.get_target_string_format()
        self.media_files = self.get_media_files()
        self.converter = self.get_converter()

    @staticmethod
    def get_script_args() -> dict:
        parser = ArgumentParser()
        parser.add_argument('--kwargs', nargs='*')

        args = parser.parse_args()

        if not args.kwargs:
            return {}
        kwargs = {}
        for kv in args.kwargs:
            k, v = kv.split('=')
            kwargs[k] = v
        return kwargs

    def get_language(self) -> str:
        KDEFAULT_LANGUAGE = self.script_args.get("LANGUAGE", self.DEFAULT_LANGUAGE)
        return getenv('OSTTC_LANGUAGE', default=KDEFAULT_LANGUAGE)

    def get_model_size(self) -> str:
        KDEFAULT_MODEL_SIZ = self.script_args.get("MODEL_SIZE", self.DEFAULT_MODEL_SIZ)
        return getenv("OSTTC_MODEL_SIZE", default=KDEFAULT_MODEL_SIZ)

    def get_path(self) -> str:
        KDEFAULT_LOCAL_PATH = self.script_args.get("PATH", self.DEFAULT_LOCAL_PATH)
        return "/data" if self.use_docker else getenv("OSTTC_LOCAL_PATH", default=KDEFAULT_LOCAL_PATH)

    def get_action_keywords(self) -> dict:
        KDEFAULT_USE_KEYWORDS = self.script_args.get("KEYWORDS", self.DEFAULT_USE_KEYWORDS)
        empty_word_map = False if int(getenv('OSTTC_KEYWORDS', default=KDEFAULT_USE_KEYWORDS)) else True
        return {} if empty_word_map else self.ACTION_KEYWORDS

    def get_use_offline(self) -> int:
        KDEFAULT_USE_OFFLINE = self.script_args.get("USE_OFFLINE", self.DEFAULT_USE_OFFLINE)
        return int(getenv("OSTTC_USE_OFFLINE", default=KDEFAULT_USE_OFFLINE))

    def get_overwrite_existing(self) -> int:
        KDEFAULT_OVERWRITE = self.script_args.get("OVERWRITE", self.DEFAULT_OVERWRITE)
        return int(getenv("OSTTC_OVERWRITE", default=KDEFAULT_OVERWRITE))

    def get_source_string_format(self) -> str:
        KDEFAULT_SOURCE_STRING = self.script_args.get("SOURCE_STRING", self.SOURCE_STRING_FORMAT)
        return getenv("OSTTC_SOURCE_STRING", default=KDEFAULT_SOURCE_STRING)

    def get_target_string_format(self) -> str:
        KDEFAULT_TARGET_STRING = self.script_args.get("TARGET_STRING", self.TARGET_STRING_FORMAT)
        return getenv("OSTTC_TARGET_STRING", default=KDEFAULT_TARGET_STRING)

    def get_media_files(self) -> list:
        KDEFAULT_MEDIA_FILES = self.script_args.get("MEDIA_FILES", self.MEDIA_FILES)
        return getenv("OSTTC_MEDIA_FILES", default=KDEFAULT_MEDIA_FILES).split(',')

    def get_converter(self):
        offline_whisper = GetTextFromAudioWhisper(self.language, self.model_size, action_keywords=self.action_keywords)
        glang_code = self.language
        if len(glang_code)==2:
            glang_code = "-".join([self.language, self.language.upper()])
        online_google = GetTextFromAudioGoogle(glang_code, action_keywords=self.action_keywords)
        converter = offline_whisper if self.use_offline else online_google
        return converter


class ObsidianSpeechToTextConverter:
    def __init__(self, config: Config):
        self.input_folder = config.path
        self.overwrite_existing = config.overwrite_existing
        self.media_files = config.media_files
        self.source_string_format = config.source_string
        self.target_string_format = config.target_string
        if not issubclass(type(config.converter), GetTextFromAudio):
            raise Exception(f"Invalid model supplied. {type(config.converter)} is not extending from GetTextFromAudio")
        self.active_model = config.converter

    def get_markdown_file_name(self, source_filename: str, root: str) -> str:
        datetime_object = datetime.strptime(source_filename, self.source_string_format)
        out_filename = datetime_object.strftime(self.target_string_format)
        return join(root, out_filename)

    def convert(self) -> None:
        if not self.active_model:
            error("Can't convert, no active model found")
            raise Exception("Can't convert, no active model found")

        for root, dirs, files in walk(self.input_folder):
            for file in files:
                tmp_filename, file_extension = splitext(basename(file))
                if file_extension not in self.media_files:
                    if file_extension not in [".md"] and file not in [".gitignore"]:
                        info(f"Skipping: '{file}' has no matching file extension ({', '.join(self.media_files)})")
                    continue

                out_file = self.get_markdown_file_name(tmp_filename, root)

                if exists(out_file) and not self.overwrite_existing:
                    info(f"Skipping: '{out_file}' already exists")
                    continue

                audio_file = str(join(root, file))
                content = self.transcribe(audio_file)
                self.create_transcription_file(out_file, content)
        info("Converting finished")

    def transcribe(self, audio_file: str) -> str:
        info(f"Transcribing: '{basename(audio_file)}'")
        return self.active_model.transcribe(audio_file)

    def create_transcription_file(self, out_file:str, content:str) -> None:
        info(f"Saving transcription to: '{out_file}'")
        with open(out_file, "w") as f:
            f.write(content)


if __name__ == "__main__":
    # Instantiation & execution of converter
    config = Config()
    obsidian_converter = ObsidianSpeechToTextConverter(config)
    obsidian_converter.convert()
