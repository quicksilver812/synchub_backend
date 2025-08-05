from .base_loader import BaseLoader
from .loader_registry import register_loader

@register_loader
class FakeWorkdayLoader(BaseLoader):
    def name(self):
        return "FakeWorkday"

    def load(self):
        return [
            {"id":"001", "name":"Ramesh", "sal":12000},
            {"id":"002", "name":"Sita", "sal":10000}
        ]
