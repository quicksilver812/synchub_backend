from .base_loader import BaseLoader
from .loader_registry import loader_registry

class FakeWorkdayLoader(BaseLoader):
    def name(self):
        return "FakeWorkday"

    def load(self):
        return [
            {"id":"001", "name":"Ramesh", "sal":12000},
            {"id":"002", "name":"Sita", "sal":10000}
        ]

loader_registry.register(FakeWorkdayLoader())