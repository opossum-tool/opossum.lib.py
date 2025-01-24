# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

from opossum_lib.opossum.opossum_file_content import OpossumFileContent
from opossum_lib.opossum.opossum_file_to_opossum_converter import (
    convert_to_opossum,
)


def read_opossum_file(filename: str) -> OpossumFileContent:
    opossum_input_file = OpossumFileContent.from_file(file_name=filename)
    opossum = convert_to_opossum(opossum_input_file)

    return opossum.to_opossum_file_format()
