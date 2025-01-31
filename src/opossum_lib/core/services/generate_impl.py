# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

from opossum_lib.core.services.input_reader import InputReader
from opossum_lib.core.services.write_opossum_file import write_opossum_file


def generate_impl(input_readers: list[InputReader], output_file: Path) -> None:
    # currently this converts only one file (validated in the arguments)
    # for the future a merge step is planned after reading the files
    opossum = input_readers[0].read()

    opossum_file_content = opossum.to_opossum_file_model()
    write_opossum_file(opossum_file_content, output_file)
