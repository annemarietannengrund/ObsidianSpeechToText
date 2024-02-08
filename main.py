from logging import basicConfig, INFO
from src.Config import Config
from src.Converter import ObsidianSpeechToTextConverter

if __name__ == "__main__":
    basicConfig(level=INFO)
    config = Config()
    obsidian_converter = ObsidianSpeechToTextConverter(config)
    obsidian_converter.convert()
