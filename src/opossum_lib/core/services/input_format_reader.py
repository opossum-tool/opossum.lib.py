# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

from abc import abstractmethod
from pathlib import Path
from typing import Protocol

from opossum_lib.core.entities.opossum_model import Opossum


class InputFormatReader(Protocol):
    @abstractmethod
    def read(self, path: Path) -> Opossum: ...
