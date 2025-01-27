# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
import sys
from pathlib import Path

from opossum_lib.opossum.file_generation import OpossumFileWriter
from opossum_lib.opossum.opossum_file_content import OpossumFileContent
from opossum_lib.opossum.read_opossum_file import read_opossum_file
from opossum_lib.scancode.convert_scancode_to_opossum import (
    convert_scancode_file_to_opossum,
)
from opossum_lib.spdx.convert_to_opossum import convert_spdx_to_opossum_information


class OpossumGenerator:
    @staticmethod
    def generate(
        spdx_files: list[str],
        scancode_json_files: list[str],
        opossum_files: list[str],
        outfile: str,
    ) -> None:
        """
        Generate an Opossum file from various other file formats.

        \b
        Currently supported input formats:
          - SPDX
          - ScanCode
          - Opossum
        """
        OpossumGenerator.validate_input_and_exit_on_error(
            spdx_files, scancode_json_files, opossum_files
        )
        opossum_file_content = OpossumGenerator.convert_after_valid_input(
            spdx_files, scancode_json_files, opossum_files
        )

        if not outfile.endswith(".opossum"):
            outfile += ".opossum"

        if Path.is_file(Path(outfile)):
            logging.warning(f"{outfile} already exists and will be overwritten.")

        OpossumFileWriter.write_opossum_information_to_file(
            opossum_file_content, Path(outfile)
        )

    @staticmethod
    def validate_input_and_exit_on_error(
        spdx_files: list[str], scancode_json_files: list[str], opossum_files: list[str]
    ) -> None:
        total_number_of_files = (
            len(spdx_files) + len(scancode_json_files) + len(opossum_files)
        )
        if total_number_of_files == 0:
            logging.warning("No input provided. Exiting.")
            sys.exit(1)
        if total_number_of_files > 1:
            logging.error("Merging of multiple files not yet supported!")
            sys.exit(1)

    @staticmethod
    def convert_after_valid_input(
        spdx_files: list[str], scancode_json_files: list[str], opossum_files: list[str]
    ) -> OpossumFileContent:
        if len(spdx_files) == 1:
            spdx_input_file = spdx_files[0]
            return convert_spdx_to_opossum_information(spdx_input_file)
        elif len(scancode_json_files) == 1:
            scancode_json_input_file = scancode_json_files[0]
            return convert_scancode_file_to_opossum(scancode_json_input_file)
        else:
            opossum_input_file = opossum_files[0]
            return read_opossum_file(opossum_input_file)
