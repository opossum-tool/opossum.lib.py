# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from opossum_lib.core.input_file import InputFileType
from opossum_lib.core.input_format_reader import InputFormatReader
from opossum_lib.core.input_reader import InputReader
from opossum_lib.core.opossum_generation_arguments import OpossumGenerationArguments
from opossum_lib.opossum_file_model.opossum_file_writer import OpossumFileWriter


class OpossumGenerator:
    input_reader: InputReader

    def __init__(self, input_format_readers: dict[InputFileType, InputFormatReader]):
        self.input_reader = InputReader(input_format_readers)

    def generate(
        self, opossum_generation_arguments: OpossumGenerationArguments
    ) -> None:
        input_files = opossum_generation_arguments.valid_input_files

        opossum = self.input_reader.read(input_files[0])

        opossum_file_content = opossum.to_opossum_file_format()
        OpossumFileWriter.write(
            opossum_file_content, opossum_generation_arguments.outfile
        )
