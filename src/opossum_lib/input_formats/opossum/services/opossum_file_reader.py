# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

from opossum_lib.core.entities.opossum import Opossum
from opossum_lib.core.services.input_reader import InputReader
from opossum_lib.input_formats.opossum.services.convert_to_opossum import (  # noqa: E501
    convert_to_opossum,
)
from opossum_lib.input_formats.opossum.services.read_opossum_file import (
    read_opossum_file,
)


class OpossumFileReader(InputReader):
    path: Path

    def __init__(self, path: Path):
        self.path = path

    def read(self) -> Opossum:
        opossum_input_file = read_opossum_file(path=self.path)
        return convert_to_opossum(opossum_input_file)
