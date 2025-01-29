# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
import logging
import sys
from pathlib import Path

from pydantic import BaseModel

from opossum_lib.core.entities.input_file import InputFile, InputFileType
from opossum_lib.core.services.input_reader import InputFormatReader, InputReader
from opossum_lib.core.services.opossum_file_writer import OpossumFileWriter


class OpossumGenerationArguments(BaseModel):
    scancode_json_files: list[Path]
    opossum_files: list[Path]
    outfile: Path

    @property
    def input_files(self) -> list[InputFile]:
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
        total_number_of_files = len(self.scancode_json_files) + len(self.opossum_files)
        if total_number_of_files == 0:
            logging.warning("No input provided. Exiting.")
            sys.exit(1)
        if total_number_of_files > 1:
            logging.error("Merging of multiple files not yet supported!")
            sys.exit(1)


class OpossumGenerator:
    input_reader: InputReader

    def __init__(self, input_format_readers: dict[InputFileType, InputFormatReader]):
        self.input_reader = InputReader(input_format_readers)

    def generate(
        self, opossum_generation_arguments: OpossumGenerationArguments
    ) -> None:
        input_files = opossum_generation_arguments.input_files

        # currently this converts only one file (validated in the arguments)
        # for the future a merge step is planned after reading the files
        opossum = self.input_reader.read(input_files[0])

        opossum_file_content = opossum.to_opossum_model()
        OpossumFileWriter.write(
            opossum_file_content, opossum_generation_arguments.outfile
        )
