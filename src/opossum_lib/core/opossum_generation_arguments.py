# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
import sys
from pathlib import Path

from pydantic import BaseModel

from opossum_lib.core.input_file import FileType, InputFile


class OpossumGenerationArguments(BaseModel):
    scancode_json_files: list[str]
    opossum_files: list[str]
    outfile: str

    def validate_input_and_exit_on_error(self) -> None:
        total_number_of_files = +len(self.scancode_json_files) + len(self.opossum_files)
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

    def generate_input_file_list(self) -> list[InputFile]:
        result = []
        result += [
            InputFile(path=path, type=FileType.SCAN_CODE)
            for path in self.scancode_json_files
        ]
        result += [
            InputFile(path=path, type=FileType.OPOSSUM) for path in self.opossum_files
        ]
        return result
