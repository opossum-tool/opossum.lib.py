# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

from opossum_lib.core.input_file import FileType
from opossum_lib.core.input_format_reader import InputFormatReader
from opossum_lib.core.opossum_model import Opossum
from opossum_lib.opossum.opossum_file_content import OpossumFileContent
from opossum_lib.opossum.opossum_file_to_opossum_converter import (
    OpossumFileToOpossumConverter,
)


class OpossumFormatReader(InputFormatReader):
    def can_handle(self, file_type: FileType) -> bool:
        return file_type == FileType.OPOSSUM

    def read(self, path: str) -> Opossum:
        opossum_input_file = OpossumFileContent.from_file(file_name=path)
        return OpossumFileToOpossumConverter.convert_to_opossum(opossum_input_file)
