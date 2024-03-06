from abc import ABC, abstractmethod
from docx import Document
import pdfplumber
from dataclasses import dataclass


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


class PdfParser(BaseParser):
    def parse(self, filepath):
        with pdfplumber.open(filepath) as pdf:
            content = ''.join([page.extract_text() for page in pdf.pages])
            metadata = pdf.metadata
        return ParsedData(content, filepath.split("/")[-1], filepath, metadata)


class TxtParser(BaseParser):
    def parse(self, filepath):
        with open(filepath, "r") as file:
            return ParsedData(file.read(), filepath.split("/")[-1], filepath, {})


class ParserFactory:
    _parsers = {}

    @classmethod
    def register_parser(cls, extension, parser):
        cls._parsers[extension] = parser

    @classmethod
    def get_parser(cls, extension):
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
