from abc import ABC, abstractmethod
from re import sub, IGNORECASE, search, DOTALL, split


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