# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from abc import abstractmethod
from asyncio import Protocol

from opossum_lib.core.entities.opossum import Opossum


class InputReader(Protocol):
    @abstractmethod
    def read(self) -> Opossum: ...
