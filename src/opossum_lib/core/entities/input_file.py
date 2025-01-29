# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from enum import IntEnum, auto
from pathlib import Path

from pydantic import BaseModel


class InputFileType(IntEnum):
    OPOSSUM = (auto(),)
    SCAN_CODE = (auto(),)


class InputFile(BaseModel):
    path: Path
    type: InputFileType
