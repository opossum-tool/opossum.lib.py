# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from opossum_lib.core.input_reader import InputReader
from opossum_lib.core.opossum_generation_arguments import OpossumGenerationArguments
from opossum_lib.opossum.file_generation import OpossumFileWriter


class OpossumGenerator:
    input_reader: InputReader = InputReader()

    def generate(
        self, opossum_generation_arguments: OpossumGenerationArguments
    ) -> None:
        opossum_generation_arguments.validate_input_and_exit_on_error()
        input_files = opossum_generation_arguments.generate_input_file_list()

        opossum = self.input_reader.read(input_files[0])

        opossum_file_content = opossum.to_opossum_file_format()
        opossum_generation_arguments.add_outfile_ending_and_warn_on_existing_outfile()
        OpossumFileWriter.write(
            opossum_file_content, Path(opossum_generation_arguments.outfile)
        )
