from abc import ABC, abstractmethod
import json
from dataclasses import dataclass

import pdfplumber


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

    def get_file_properties(self, filepath: str, mapping_file_path: str) -> tuple[str, str]:
        parts = filepath.split("/")[-1].rsplit("_", 1)
        file_name_with_underscores, hash_and_ext = parts
        hash_part, file_ext = hash_and_ext.split(".")

        full_file_name = f"{file_name_with_underscores}.{file_ext}"

        file_url = find_url_hash_mapping(hash_part[:10], mapping_file_path)  # Using first 10 characters of the hash

        return file_url, full_file_name


class PdfParser(BaseParser):
    def parse(self, filepath):
        with pdfplumber.open(filepath) as pdf:
            content = ''.join([page.extract_text() for page in pdf.pages])
            metadata = pdf.metadata

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
