from .base_loader import BaseLoader
from .loader_registry import loader_registry

class CSVLoader(BaseLoader):
    def __init__(self):
        self._records = []
        self._source_name = "CSV"

    def name(self):
        return self._source_name

    def set_data(self, name: str, records: list[dict]):
        self._source_name = name
        self._records = records

    def load(self):
        return self._records

loader_registry.register(CSVLoader())