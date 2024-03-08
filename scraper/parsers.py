from abc import ABC, abstractmethod
import json
from dataclasses import dataclass

from llama_parse import LlamaParse

from scraper import config


def find_url_hash_mapping(url_hash: str) -> str:
    """
    Find original url from url_hash
    """
    mapping_file = "url_hash_mapping.json"
    try:
        with open(mapping_file, "r") as f:
            mapping = json.load(f)
    except FileNotFoundError:
        return None

    return mapping.get(url_hash)


@dataclass
class ParsedData:
    content: str
    filename: str
    path: str
    metadata: dict


class BaseParser(ABC):
    @abstractmethod
    def parse(self, filepath: str) -> ParsedData:
        pass

    def get_file_properties(self, filepath: str):
        url_hash = filepath.split("/")[-1].split(".")[0].split("_")[-1]
        file_url = find_url_hash_mapping(url_hash)
        file_ext = filepath.split("/")[-1].split(".")[-1]
        file_name = filepath.split("/")[-1].split(".")[0].split("_")[0] + "." + file_ext

        return file_url, file_name


class PdfParser(BaseParser):
    parser = LlamaParse(verbose=True, api_key=config.LLAMA_PARSE_API_KEY)

    def parse(self, filepath):
        json_objs = self.parser.get_json_result(filepath)

        if json_objs and "pages" in json_objs[0]:
            content = "".join([page.get("text", "") for page in json_objs[0]["pages"]])
        else:
            content = ""

        metadata = json_objs[0].get("metadata", {})

        file_url, file_name = self.get_file_properties(filepath)

        return ParsedData(content, file_name, file_url, metadata)


class TxtParser(BaseParser):
    def parse(self, filepath):
        with open(filepath, "r") as file:
            file_url, file_name = self.get_file_properties(filepath)

            return ParsedData(file.read(), file_name, file_url, {})


class ParserFactory:
    _parsers = {}

    @classmethod
    def register_parser(cls, extension, parser):
        cls._parsers[extension] = parser

    @classmethod
    def get_parser(cls, extension):
        extension = extension.lower()
        extension = extension.split("_")[0]
        parser = cls._parsers.get(extension)
        if not parser:
            raise ValueError(f"No parser found for extension: {extension}")
        return parser()


ParserFactory.register_parser("pdf", PdfParser)
ParserFactory.register_parser("txt", TxtParser)
ParserFactory.register_parser("json", TxtParser)


class FileParser:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.parser = self._get_parser()

    def _get_parser(self) -> BaseParser:
        extension = self.filepath.split(".")[-1]
        return ParserFactory.get_parser(extension)

    def parse(self) -> ParsedData:
        return self.parser.parse(self.filepath)
