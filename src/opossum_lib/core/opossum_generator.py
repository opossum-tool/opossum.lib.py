# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0


from opossum_lib.core.input_reader import InputReader
from opossum_lib.core.opossum_generation_arguments import OpossumGenerationArguments
from opossum_lib.input_formats.opossum.opossum_file_writer import OpossumFileWriter


class OpossumGenerator:
    input_reader: InputReader = InputReader()

    def generate(
        self, opossum_generation_arguments: OpossumGenerationArguments
    ) -> None:
        opossum_generation_arguments.validate_and_exit_on_error()
        input_files = opossum_generation_arguments.input_files

        opossum = self.input_reader.read(input_files[0])

        opossum_file_content = opossum.to_opossum_file_format()
        OpossumFileWriter.write(
            opossum_file_content, opossum_generation_arguments.outfile
        )
