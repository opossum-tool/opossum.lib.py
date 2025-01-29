# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from pydantic import BaseModel

from opossum_lib.opossum_file_model.opossum_file import OpossumInformation
from opossum_lib.opossum_file_model.output_model import OpossumOutputFile


class OpossumFileContent(BaseModel):
    input_file: OpossumInformation
    output_file: OpossumOutputFile | None = None
