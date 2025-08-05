from typing import Dict
from .base_loader import BaseLoader

class LoaderRegistry:
    def __init__(self):
        self._registry: Dict[str, BaseLoader] = {}

    def register(self, loader: BaseLoader):
        self._registry[loader.name()] = loader

    def get(self, name: str) -> BaseLoader:
        return self._registry.get(name)

    def all(self) -> Dict[str, BaseLoader]:
        return self._registry

    def exists(self, name: str) -> bool:
        return name in self._registry

    def remove(self, name: str):
        if name in self._registry:
            del self._registry[name]

# Global instance
loader_registry = LoaderRegistry()