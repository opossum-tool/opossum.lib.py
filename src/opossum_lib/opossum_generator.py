# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
import sys
from pathlib import Path

from pydantic import BaseModel

from opossum_lib.opossum.file_generation import OpossumFileWriter
from opossum_lib.opossum.opossum_file_content import OpossumFileContent
from opossum_lib.opossum.read_opossum_file import read_opossum_file
from opossum_lib.scancode.convert_scancode_to_opossum import (
    convert_scancode_file_to_opossum,
)
from opossum_lib.spdx.convert_to_opossum import convert_spdx_to_opossum_information


class OpossumGenerationArguments(BaseModel):
    spdx_files: list[str]
    scancode_json_files: list[str]
    opossum_files: list[str]
    outfile: str

    def validate_input_and_exit_on_error(self) -> None:
        total_number_of_files = (
            len(self.spdx_files)
            + len(self.scancode_json_files)
            + len(self.opossum_files)
        )
        if total_number_of_files == 0:
            logging.warning("No input provided. Exiting.")
            sys.exit(1)
        if total_number_of_files > 1:
            logging.error("Merging of multiple files not yet supported!")
            sys.exit(1)

    def add_outfile_ending_and_warn_on_existing_outfile(self) -> None:
        if not self.outfile.endswith(".opossum"):
            self.outfile += ".opossum"

        if Path.is_file(Path(self.outfile)):
            logging.warning(f"{self.outfile} already exists and will be overwritten.")


class OpossumGenerator:
    @staticmethod
    def generate(opossum_generation_arguments: OpossumGenerationArguments) -> None:
        """
        Generate an Opossum file from various other file formats.

        \b
        Currently supported input formats:
          - SPDX
          - ScanCode
          - Opossum
        """
        opossum_generation_arguments.validate_input_and_exit_on_error()
        opossum_file_content = OpossumGenerator.convert_after_valid_input(
            opossum_generation_arguments
        )
        opossum_generation_arguments.add_outfile_ending_and_warn_on_existing_outfile()

        OpossumFileWriter.write_opossum_information_to_file(
            opossum_file_content, Path(opossum_generation_arguments.outfile)
        )

    @staticmethod
    def convert_after_valid_input(
        opossum_generation_arguments: OpossumGenerationArguments,
    ) -> OpossumFileContent:
        if len(opossum_generation_arguments.spdx_files) == 1:
            spdx_input_file = opossum_generation_arguments.spdx_files[0]
            return convert_spdx_to_opossum_information(spdx_input_file)
        elif len(opossum_generation_arguments.scancode_json_files) == 1:
            scancode_json_input_file = opossum_generation_arguments.scancode_json_files[
                0
            ]
            return convert_scancode_file_to_opossum(scancode_json_input_file)
        else:
            opossum_input_file = opossum_generation_arguments.opossum_files[0]
            return read_opossum_file(opossum_input_file)
