# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import sys

from opossum_lib.core.input_file import FileType
from opossum_lib.core.input_format_reader import InputFormatReader
from opossum_lib.core.opossum_model import (
    Opossum,
)
from opossum_lib.scancode.model import ScanCodeData
from opossum_lib.scancode.scancode_data_to_opossum_converter import (
    ScancodeDataToOpossumConverter,
)


class ScancodeFormatReader(InputFormatReader):
    def can_handle(self, file_type: FileType) -> bool:
        return file_type == FileType.SCAN_CODE

    def read(self, path: str) -> Opossum:
        logging.info(f"Converting scancode to opossum {path}")

        scancode_data = ScancodeFormatReader.load_scancode_json(path)

        return ScancodeDataToOpossumConverter.convert_scancode_to_opossum(scancode_data)

    @staticmethod
    def load_scancode_json(filename: str) -> ScanCodeData:
        try:
            with open(filename) as inp:
                json_data = json.load(inp)
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding json for file {filename}. Message: {e.msg}")
            sys.exit(1)
        except UnicodeDecodeError:
            logging.error(f"Error decoding json for file {filename}.")
            sys.exit(1)

        scancode_data = ScanCodeData.model_validate(json_data)

        return scancode_data
