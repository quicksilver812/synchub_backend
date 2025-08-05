from .base_loader import BaseLoader
from .loader_registry import register_loader

@register_loader
class FakeSAPLoader(BaseLoader):
    def name(self):
        return "FakeSAP"

    def load(self):
        return [
            {"emp_id":"001", "emp_sal":12000, "emp_name":"Ramesh"},
            {"emp_id":"002", "emp_sal":10000, "emp_name":"Sita"}
        ]
