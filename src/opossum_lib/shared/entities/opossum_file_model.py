# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from pydantic import BaseModel

from opossum_lib.shared.entities.opossum_input_file_model import OpossumInputFileModel
from opossum_lib.shared.entities.opossum_output_file_model import OpossumOutputFileModel


class OpossumFileModel(BaseModel):
    input_file: OpossumInputFileModel
    output_file: OpossumOutputFileModel | None = None
