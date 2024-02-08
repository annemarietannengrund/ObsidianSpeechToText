from argparse import ArgumentParser
from os import getenv
from logging import info
from src.processor.Whisper import Whisper
from dotenv import load_dotenv

load_dotenv()

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
        f"[.,]?\\s{ACTION_KEYWORD}[-,\\s]+?({ACTION_TYPE_TAGS})[s]?[.,\\s]? ({ACTION_STOP_WORDS})[.,]?\\s?": " ---TAGS#",

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
        return Whisper(self.language, self.model_size, action_keywords=self.action_keywords)
