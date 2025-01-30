# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

import json
import logging
import sys
from pathlib import Path

from opossum_lib.core.entities.opossum import (
    Opossum,
)
from opossum_lib.core.services.input_reader import InputReader
from opossum_lib.input_formats.scancode.entities.scan_code_data_model import (
    ScanCodeDataModel,
)
from opossum_lib.input_formats.scancode.services.convert_scancode_to_opossum import (
    convert_scancode_to_opossum,
)


class ScancodeFileReader(InputReader):
    def __init__(self, path: Path):
        self.path = path

    def read(self) -> Opossum:
        logging.info(f"Converting scancode to opossum {self.path}")

        scancode_data = self._load_scancode_json()

        return convert_scancode_to_opossum(scancode_data)

    def _load_scancode_json(self) -> ScanCodeDataModel:
        try:
            with open(self.path) as inp:
                json_data = json.load(inp)
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding json for file {self.path}. Message: {e.msg}")
            sys.exit(1)
        except UnicodeDecodeError:
            logging.error(f"Error decoding json for file {self.path}.")
            sys.exit(1)

        scancode_data = ScanCodeDataModel.model_validate(json_data)

        return scancode_data
