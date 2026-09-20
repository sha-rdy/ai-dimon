from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from DocumentTypes import BaseDocument

In = TypeVar("In",bound=BaseDocument)
Out = TypeVar("Out",bound=BaseDocument)


class IConverter(ABC, Generic[In, Out]):
    @abstractmethod
    def convert(self, source: In, target: Out) -> None:
        ...


class ConverterError(RuntimeError):
    ...