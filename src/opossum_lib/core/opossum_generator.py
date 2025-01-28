# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from opossum_lib.core.input_file import FileType, InputFile
from opossum_lib.core.opossum_generation_arguments import OpossumGenerationArguments
from opossum_lib.opossum.file_generation import OpossumFileWriter
from opossum_lib.opossum.opossum_file_content import OpossumFileContent
from opossum_lib.opossum.read_opossum_file import read_opossum_file
from opossum_lib.scancode.convert_scancode_to_opossum import (
    convert_scancode_file_to_opossum,
)
from opossum_lib.spdx.convert_to_opossum import convert_spdx_to_opossum_information


class OpossumGenerator:
    @staticmethod
    def generate(opossum_generation_arguments: OpossumGenerationArguments) -> None:
        opossum_generation_arguments.validate_input_and_exit_on_error()
        input_files = opossum_generation_arguments.generate_input_file_list()
        opossum_generation_arguments.add_outfile_ending_and_warn_on_existing_outfile()

        opossum_file_content = OpossumGenerator._convert_after_valid_input(input_files)
        OpossumFileWriter.write_opossum_information_to_file(
            opossum_file_content, Path(opossum_generation_arguments.outfile)
        )

    @staticmethod
    def _convert_after_valid_input(
        input_file_list: list[InputFile],
    ) -> OpossumFileContent:
        input_file = input_file_list[0]

        if input_file.type == FileType.SPDX:
            return convert_spdx_to_opossum_information(input_file.path)

        elif input_file.type == FileType.SCAN_CODE:
            return convert_scancode_file_to_opossum(
                input_file.path
            ).to_opossum_file_format()
        else:
            return read_opossum_file(input_file.path)
