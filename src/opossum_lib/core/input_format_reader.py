from abc import abstractmethod
from typing import Protocol

from opossum_lib.core.input_file import FileType
from opossum_lib.core.opossum_model import Opossum


class InputFormatReader(Protocol):
    @abstractmethod
    def can_handle(self, file_type: FileType) -> bool: ...

    @abstractmethod
    def read(self, path: str) -> Opossum: ...
