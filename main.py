from abc import ABC, abstractmethod
from argparse import ArgumentParser
from datetime import datetime
from logging import basicConfig, info, error, INFO, warning
from os import walk, getenv
from os.path import join, splitext, basename, exists
from re import sub, IGNORECASE, search, DOTALL, split
from time import time

from dotenv import load_dotenv
from whisper import load_model

load_dotenv()
basicConfig(level=INFO)


class AudioTextProcessor(ABC):
    @abstractmethod
    def transcribe(self, audio_file: str):
        pass

    @abstractmethod
    def init_model(self) -> None:
        pass

    def format_text(self, text, words, audio_file_name: str) -> str:
        if not words:
            return text
        for word, format in words.items():
            text = sub(word, format, text, flags=IGNORECASE)
        text = self.format_hashtags(text)
        tags = self.get_tags_str_for_properties(text)
        text = self.remove_obsidian_tags_from_text(text)
        link_audio = self.has_audiofile_keyword(text, audio_file_name)
        audiolog = self.get_audiofile_keyword_for_properties(link_audio)
        text = self.remove_audiofile_keyword(text)

        properties = [tags, audiolog]
        info(properties)
        header = self.create_properties_header(properties, link_audio)
        return header + text

    def create_properties_header(self, properties: list, link_audio: str) -> str:
        if not properties and not link_audio:
            return ""
        if not properties and link_audio:
            return f'![[{link_audio}]]\n'

        header = "\n".join(['---', "\n".join(properties), '---\n'])
        if link_audio:
            header = "\n".join([header, f'![[{link_audio}]]\n'])

        return header

    def get_tags_str_for_properties(self, text: str) -> str:
        pattern = r"#TAGS---(.*?)---TAGS#"
        match = search(pattern, text, DOTALL)

        if not match:
            return ""
        split_list = split(r"[,\.\s]", match.group(1))
        tags = [word.capitalize() for word in split_list if word]
        if not tags:
            return ""
        tag_str = "tags:"
        for tag in tags:
            tag_str = tag_str + f"\n  - {tag}"
        return tag_str

    def get_audiofile_keyword_for_properties(self, audio_file_name: str) -> str:
        if not audio_file_name:
            return ""
        return f'audiolog: "[[{audio_file_name}]]"'

    def has_audiofile_keyword(self, text: str, audio_file_name: str) -> str:
        return audio_file_name if "#LINK_AUDIO_FILE#" in text else ""

    def remove_obsidian_tags_from_text(self, text: str) -> str:
        pattern = r"#TAGS---(.*?)---TAGS#"
        match = search(pattern, text, DOTALL)
        if not match:
            return text
        return text.replace(match.group(0), "")

    def remove_audiofile_keyword(self, text: str) -> str:
        return text.replace("#LINK_AUDIO_FILE#", '')

    def format_hashtags(self, text: str):
        pattern = r'Hashtag ([^,\.]*)[,.]?'
        return sub(pattern, lambda m: '#' + ''.join(word.capitalize() for word in m.group(1).split()), text)

    @staticmethod
    def word_counter(text: str) -> int:
        return len(text.split())


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


class Config:
    # default script configs
    DEFAULT_LANGUAGE = "de"
    DEFAULT_MODEL_SIZ = "medium"
    DEFAULT_LOCAL_PATH = "./recordings"
    DEFAULT_USE_KEYWORDS = 1
    DEFAULT_OVERWRITE = 0
    MEDIA_FILES = ",".join(['.webm', '.mp3', '.wav', '.m4a'])
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
    ACTION_KEYWORD = "obsidian"

    ACTION_TYPE_LINK = "link"
    ACTION_TYPE_TAGS = "text|tech"
    ACTION_TYPE_CITATION = "Zitat|citation"
    ACTION_TYPE_DIVIDER = "text[\s-]?teiler|text divider"
    ACTION_TYPE_HEADLINE = "überschrift|headline"
    ACTION_TYPE_LINEBREAK = "Line Break|Absatz|Zeilenumbruch"
    ACTION_TYPE_LONG_DASH = "Gedankenstrich"
    ACTION_TYPE_LIST_ELEMENT = "Listen[\\s-]?strich"
    ACTION_TYPE_CHECKED_CHECKBOX_ELEMENT = "checkbox[\\s-]item erfüllt"
    ACTION_TYPE_CHECKBOX_ELEMENT = "checkbox[\\s-]item"
    ACTION_TYPE_BADWORDS = "schei(ss|ß)e|fuck|kacke|fick|dreck(s?mist)+|mist"
    ACTION_TYPE_HASHTAG = "hashtag "
    ACTION_TYPE_AUDIO_FILE_LINK = "Link[-,.\\s]+?Audio[-,.\\s]+?File[,.]+?"

    ACTION_START_WORDS = "start|anfang|begin"
    ACTION_STOP_WORDS = "stop|ende|end"

    NEWLINE_ACTIONS = True
    NLP = "\n" if NEWLINE_ACTIONS else ""

    ACTION_KEYWORDS = {
        # pairwise instructions
        f"{ACTION_KEYWORD}[-\\s]?{ACTION_TYPE_LINK} ({ACTION_START_WORDS})[\\s.,]?\\s?": "[[",
        f"[.,]?\\s{ACTION_KEYWORD}[-\\s]?{ACTION_TYPE_LINK} ({ACTION_STOP_WORDS})[.,]?\\s?": "]] ",

        f"{ACTION_KEYWORD}[-,\\s]+?({ACTION_TYPE_TAGS})[s]?[,]? ({ACTION_START_WORDS})[\\s.,]?\\s?": "#TAGS--- ",
        f"[.,]?\\s{ACTION_KEYWORD}[-,\\s]+?({ACTION_TYPE_TAGS})[s]?[,\\s]? ({ACTION_STOP_WORDS})[.,]?\\s?": " ---TAGS#",

        # single line instructions
        f"({ACTION_TYPE_LINEBREAK})[.,]?\s?": "\n",
        f"\\s?({ACTION_TYPE_CITATION} ({ACTION_START_WORDS}))[.,]?\\s?": f"{NLP}> ",
        f"\\s?(({ACTION_TYPE_DIVIDER}) ({ACTION_START_WORDS}))[.,]?\\s?": f"{NLP}---\n",
        f"({ACTION_TYPE_HEADLINE}) H1[.,]?\\s?": f"{NLP}# ",
        f"({ACTION_TYPE_HEADLINE}) H2[.,]?\\s?": f"{NLP}## ",
        f"({ACTION_TYPE_HEADLINE}) H3[.,]?\\s?": f"{NLP}### ",
        f"({ACTION_TYPE_HEADLINE}) H4[.,]?\\s?": f"{NLP}#### ",
        f"({ACTION_TYPE_HEADLINE}) H5[.,]?\\s?": f"{NLP}##### ",
        f"({ACTION_TYPE_HEADLINE}) H6[.,]?\\s?": f"{NLP}###### ",
        f"({ACTION_TYPE_LONG_DASH})[-\\s]?({ACTION_START_WORDS})": f"{NLP}—",
        f"\\s\\s?({ACTION_TYPE_LIST_ELEMENT})[\\s.,]?": f"{NLP}- ",
        f"\\s\\s?({ACTION_TYPE_CHECKED_CHECKBOX_ELEMENT})[\\s.,]?": f"{NLP}- [x] ",
        f"\\s\\s?({ACTION_TYPE_CHECKBOX_ELEMENT})[\\s.,]?": f"{NLP}- [ ] ",
        f"({ACTION_TYPE_BADWORDS})": "💩",
        f"({ACTION_TYPE_AUDIO_FILE_LINK})": "#LINK_AUDIO_FILE#",
    }

    def __init__(self) -> None:
        self.script_args = self.get_script_args()
        self.use_docker = int(getenv("RUNS_ON_DOCKER", default="0"))
        self.language = self.get_language()
        self.model_size = self.get_model_size()
        self.path = self.get_path()
        info(f"input_folder has been configured to '{self.path}'")
        self.action_keywords = self.get_action_keywords()
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
        ENV_DEFAULT_LANGUAGE = getenv('OSTTC_LANGUAGE', default=self.DEFAULT_LANGUAGE)
        return self.script_args.get("LANGUAGE", ENV_DEFAULT_LANGUAGE)

    def get_model_size(self) -> str:
        ENV_DEFAULT_MODEL_SIZ = getenv("OSTTC_MODEL_SIZE", default=self.DEFAULT_MODEL_SIZ)
        return self.script_args.get("MODEL_SIZE", ENV_DEFAULT_MODEL_SIZ)

    def get_path(self) -> str:
        ENV_DEFAULT_LOCAL_PATH = getenv("OSTTC_LOCAL_PATH", default=self.DEFAULT_LOCAL_PATH)
        return "/data" if self.use_docker else self.script_args.get("PATH", ENV_DEFAULT_LOCAL_PATH)

    def get_action_keywords(self) -> dict:
        ENV_DEFAULT_USE_KEYWORDS = int(getenv('OSTTC_KEYWORDS', default=self.DEFAULT_USE_KEYWORDS))
        empty_word_map = False if int(self.script_args.get("KEYWORDS", ENV_DEFAULT_USE_KEYWORDS)) else True
        return {} if empty_word_map else self.ACTION_KEYWORDS

    def get_overwrite_existing(self) -> int:
        ENV_DEFAULT_OVERWRITE = getenv("OSTTC_OVERWRITE", default=self.DEFAULT_OVERWRITE)
        return int(self.script_args.get("OVERWRITE", ENV_DEFAULT_OVERWRITE))

    def get_source_string_format(self) -> str:
        ENV_DEFAULT_SOURCE_STRING = getenv("OSTTC_SOURCE_STRING", default=self.SOURCE_STRING_FORMAT)
        return self.script_args.get("SOURCE_STRING", ENV_DEFAULT_SOURCE_STRING)

    def get_target_string_format(self) -> str:
        ENV_DEFAULT_TARGET_STRING = getenv("OSTTC_TARGET_STRING", default=self.TARGET_STRING_FORMAT)
        return self.script_args.get("TARGET_STRING", ENV_DEFAULT_TARGET_STRING)

    def get_media_files(self) -> list:
        ENV_DEFAULT_MEDIA_FILES = getenv("OSTTC_MEDIA_FILES", default=self.MEDIA_FILES)
        return self.script_args.get("MEDIA_FILES", ENV_DEFAULT_MEDIA_FILES).split(',')

    def get_converter(self):
        return AudioTextProcessorWhisper(self.language, self.model_size, action_keywords=self.action_keywords)


class ObsidianSpeechToTextConverter:
    def __init__(self, config: Config):
        self.input_folder = config.path
        self.overwrite_existing = config.overwrite_existing
        self.media_files = config.media_files
        self.source_string_format = config.source_string
        self.target_string_format = config.target_string
        if not issubclass(type(config.converter), AudioTextProcessor):
            raise Exception(f"Invalid model supplied. {type(config.converter)} is not extending from GetTextFromAudio")
        self.active_model = config.converter

    def get_markdown_file_name(self, source_filename: str, root: str) -> str:
        try:
            datetime_object = datetime.strptime(source_filename, self.source_string_format)
            out_filename = datetime_object.strftime(self.target_string_format)
        except ValueError as e:
            error(e)
            warning(
                f"The provided source filename '{source_filename}' can't be parsed with '{self.source_string_format}'.")
            out_filename = "".join([source_filename, '.md'])
            info(f"falling back to original filename: '{out_filename}'")

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

    def create_transcription_file(self, out_file: str, content: str) -> None:
        info(f"Saving transcription to: '{out_file}'")
        with open(out_file, "w") as f:
            f.write(content)


if __name__ == "__main__":
    # Instantiation & execution of converter
    config = Config()
    obsidian_converter = ObsidianSpeechToTextConverter(config)
    obsidian_converter.convert()
