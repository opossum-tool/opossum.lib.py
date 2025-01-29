# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

from opossum_lib.core.entities.opossum import Opossum
from opossum_lib.core.services.input_reader import InputFormatReader
from opossum_lib.input_formats.opossum.services.opossum_file_reader import (
    OpossumFileReader,
)
from opossum_lib.input_formats.opossum.services.opossum_file_to_opossum_converter import (  # noqa: E501
    OpossumFileToOpossumConverter,
)


class OpossumFormatReader(InputFormatReader):
    def read(self, path: Path) -> Opossum:
        opossum_input_file = OpossumFileReader.from_file(path=path)
        return OpossumFileToOpossumConverter.convert_to_opossum(opossum_input_file)
