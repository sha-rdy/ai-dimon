# converter/documents/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class BaseDocument(ABC):
    """Базовый документ с метаданными."""

    metadata: dict[str, Any] = field(default_factory=dict)

    @abstractmethod
    def read(self) -> None:
        """Загрузить содержимое (из файла, из сети, из памяти)."""
        ...

    @abstractmethod
    def write(self) -> None:
        """Сохранить содержимое (в файл, в память)."""
        ...

    @property
    @abstractmethod
    def content(self) -> Any:
        """Доступ к содержимому в родном для типа виде."""
        ...