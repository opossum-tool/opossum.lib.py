# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from opossum_lib.core.services.input_reader import InputReader
from opossum_lib.core.services.opossum_file_writer import OpossumFileWriter


def generate_impl(readers: list[InputReader], outfile: str) -> None:
    # currently this converts only one file (validated in the arguments)
    # for the future a merge step is planned after reading the files
    opossum = readers[0].read()

    opossum_file_content = opossum.to_opossum_model()
    OpossumFileWriter.write(opossum_file_content, outfile)
