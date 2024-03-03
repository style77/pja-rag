from abc import ABC, abstractmethod
from docx import Document
import openpyxl
import pdfplumber


class BaseParser(ABC):
    @abstractmethod
    def parse(self, filepath):
        pass


class DocxParser(BaseParser):
    def parse(self, filepath):
        document = Document(filepath)
        return "\n".join([paragraph.text for paragraph in document.paragraphs])


class PdfParser(BaseParser):
    def parse(self, filepath):
        with pdfplumber.open(filepath) as pdf:
            content = ''.join([page.extract_text() for page in pdf.pages])
            return content


class TxtParser(BaseParser):
    def parse(self, filepath):
        with open(filepath, "r") as file:
            return file.read()


class XlsxParser(BaseParser):
    def parse(self, filepath):
        workbook = openpyxl.load_workbook(filepath)
        content = ""
        for sheet in workbook.sheetnames:
            worksheet = workbook[sheet]
            for row in worksheet.iter_rows(values_only=True):
                content += "\n" + ", ".join(
                    [str(cell) if cell is not None else "" for cell in row]
                )
        return content


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
# ParserFactory.register_parser("txt", TxtParser)
# ParserFactory.register_parser("json", TxtParser)
# ParserFactory.register_parser("docx", DocxParser)
# ParserFactory.register_parser("xlsx", XlsxParser)
# ParserFactory.register_parser("xls", XlsxParser)


class FileParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.parser = self._get_parser()

    def _get_parser(self):
        extension = self.filepath.split(".")[-1]
        return ParserFactory.get_parser(extension)

    def parse(self):
        return self.parser.parse(self.filepath)
