# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

from opossum_lib.core.input_file import InputFileType
from opossum_lib.core.input_format_reader import InputFormatReader
from opossum_lib.core.opossum_model import Opossum
from opossum_lib.input_formats.opossum.opossum_file_content import OpossumFileContent
from opossum_lib.input_formats.opossum.opossum_file_to_opossum_converter import (
    OpossumFileToOpossumConverter,
)


class OpossumFormatReader(InputFormatReader):
    def can_handle(self, file_type: InputFileType) -> bool:
        return file_type == InputFileType.OPOSSUM

    def read(self, path: Path) -> Opossum:
        opossum_input_file = OpossumFileContent.from_file(path=path)
        return OpossumFileToOpossumConverter.convert_to_opossum(opossum_input_file)
