from abc import ABC, abstractmethod

class BaseLoader(ABC):
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def load(self) -> list[dict]:
        ...
