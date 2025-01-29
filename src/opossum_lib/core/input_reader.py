# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

from opossum_lib.core.input_file import InputFile, InputFileType
from opossum_lib.core.input_format_reader import InputFormatReader
from opossum_lib.core.opossum_model import Opossum


class InputReader:
    input_format_readers: dict[InputFileType, InputFormatReader]

    def __init__(self, input_format_readers: dict[InputFileType, InputFormatReader]):
        self.input_format_readers = input_format_readers

    def read(self, input_file: InputFile) -> Opossum:
        if input_file.type in self.input_format_readers:
            return self.input_format_readers[input_file.type].read(input_file.path)
        raise NotImplementedError(f"Unsupported file type: {input_file.type}")
