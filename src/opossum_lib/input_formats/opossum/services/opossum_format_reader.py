# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

from opossum_lib.core.entities.opossum import Opossum
from opossum_lib.core.services.input_reader import InputReader
from opossum_lib.input_formats.opossum.services.opossum_file_model_to_opossum_converter import (  # noqa: E501
    OpossumFileModelToOpossumConverter,
)
from opossum_lib.input_formats.opossum.services.opossum_file_reader import (
    OpossumFileReader,
)


class OpossumFormatReader(InputReader):
    path: Path

    def __init__(self, path: Path):
        self.path = path

    def read(self) -> Opossum:
        opossum_input_file = OpossumFileReader.from_file(path=self.path)
        return OpossumFileModelToOpossumConverter.convert_to_opossum(opossum_input_file)
