# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
import sys
from pathlib import Path

from pydantic import BaseModel

from opossum_lib.core.entities.input_file import InputFile, InputFileType


class OpossumGenerationArguments(BaseModel):
    scancode_json_files: list[Path]
    opossum_files: list[Path]
    outfile: Path

    @property
    def valid_input_files(self) -> list[InputFile]:
        self._validate_and_exit_on_error()
        result = []
        result += [
            InputFile(path=path, type=InputFileType.SCAN_CODE)
            for path in self.scancode_json_files
        ]
        result += [
            InputFile(path=path, type=InputFileType.OPOSSUM)
            for path in self.opossum_files
        ]
        return result

    def _validate_and_exit_on_error(self) -> None:
        total_number_of_files = +len(self.scancode_json_files) + len(self.opossum_files)
        if total_number_of_files == 0:
            logging.warning("No input provided. Exiting.")
            sys.exit(1)
        if total_number_of_files > 1:
            logging.error("Merging of multiple files not yet supported!")
            sys.exit(1)
