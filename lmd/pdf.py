from typing import Literal
from pypdf import PdfWriter, PdfReader

class Generator:
    def __init__(self, _type: Literal["diocesis", "civil_registry"]) -> None:
        self.file = None

    def read(self, ):
        _reader = PdfReader(self.file)
        for page in _reader.pages:
            print(page.extract_text())

    def write(self,):
        _reader = PdfReader(self.file)
        for page in _reader.pages:
            print(page.extract_text())