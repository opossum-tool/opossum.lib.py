# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import sys
from pathlib import Path

from opossum_lib.core.entities.opossum_model import (
    Opossum,
)
from opossum_lib.core.services.input_format_reader import InputFormatReader
from opossum_lib.input_formats.scancode.entities.model import ScanCodeData
from opossum_lib.input_formats.scancode.services.scancode_data_to_opossum_converter import (  # noqa: E501
    ScancodeDataToOpossumConverter,
)


class ScancodeFormatReader(InputFormatReader):
    def read(self, path: Path) -> Opossum:
        logging.info(f"Converting scancode to opossum {path}")

        scancode_data = ScancodeFormatReader.load_scancode_json(path)

        return ScancodeDataToOpossumConverter.convert_scancode_to_opossum(scancode_data)

    @staticmethod
    def load_scancode_json(path: Path) -> ScanCodeData:
        try:
            with open(path) as inp:
                json_data = json.load(inp)
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding json for file {path}. Message: {e.msg}")
            sys.exit(1)
        except UnicodeDecodeError:
            logging.error(f"Error decoding json for file {path}.")
            sys.exit(1)

        scancode_data = ScanCodeData.model_validate(json_data)

        return scancode_data
