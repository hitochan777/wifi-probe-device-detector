import abc
from typing import Generator

class Queue(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def is_empty(self) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_items(self) -> Generator[str, None, None]:
        raise NotImplementedError()

    @abc.abstractmethod
    def enqueue(self, value: str) -> None:
        raise NotImplementedError()