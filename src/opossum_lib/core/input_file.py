# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from enum import Enum, auto

from pydantic import BaseModel


class FileType(Enum):
    OPOSSUM = (auto(),)
    SCAN_CODE = (auto(),)


class InputFile(BaseModel):
    path: str
    type: FileType
