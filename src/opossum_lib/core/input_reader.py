# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

from opossum_lib.core.input_file import InputFile, InputFileType
from opossum_lib.core.input_format_reader import InputFormatReader
from opossum_lib.core.opossum_model import Opossum
from opossum_lib.input_formats.opossum.opossum_format_reader import OpossumFormatReader
from opossum_lib.input_formats.scancode.scancode_format_reader import (
    ScancodeFormatReader,
)


class InputReader:
    input_format_readers: dict[InputFileType, InputFormatReader] = {
        InputFileType.OPOSSUM: OpossumFormatReader(),
        InputFileType.SCAN_CODE: ScancodeFormatReader(),
    }

    def read(self, input_file: InputFile) -> Opossum:
        if input_file.type in self.input_format_readers:
            return self.input_format_readers[input_file.type].read(input_file.path)
        raise NotImplementedError(f"Unsupported file type: {input_file.type}")
