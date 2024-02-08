from src.Config import Config
from src.abstracts.AudioTextProcessor import AudioTextProcessor
from datetime import datetime
from logging import info, error, warning
from os import walk
from os.path import join, splitext, basename, exists


class ObsidianSpeechToTextConverter:
    def __init__(self, config: Config):
        self.input_folder = config.path
        self.overwrite_existing = config.overwrite_existing
        self.media_files = config.media_files
        self.source_string_format = config.source_string
        self.target_string_format = config.target_string

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