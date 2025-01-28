# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

from opossum_lib.core.input_file import InputFile
from opossum_lib.core.input_format_reader import InputFormatReader
from opossum_lib.core.opossum_model import Opossum
from opossum_lib.input_formats.opossum.opossum_format_reader import OpossumFormatReader
from opossum_lib.input_formats.scancode.scancode_format_reader import (
    ScancodeFormatReader,
)


class InputReader:
    input_format_readers: list[InputFormatReader] = [
        OpossumFormatReader(),
        ScancodeFormatReader(),
    ]

    def read(self, input_file: InputFile) -> Opossum:
        for input_format_reader in self.input_format_readers:
            if input_format_reader.can_handle(input_file.type):
                return input_format_reader.read(input_file.path)
        raise NotImplementedError(f"Unsupported file type: {input_file.type}")
