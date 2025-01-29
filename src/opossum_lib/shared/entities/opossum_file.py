# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from pydantic import BaseModel

from opossum_lib.shared.entities.opossum_input_file import OpossumInputFile
from opossum_lib.shared.entities.opossum_output_file import OpossumOutputFile


class OpossumFileModel(BaseModel):
    input_file: OpossumInputFile
    output_file: OpossumOutputFile | None = None
