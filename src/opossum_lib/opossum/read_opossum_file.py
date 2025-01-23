# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

from opossum_lib.opossum.opossum_file_content import OpossumFileContent


def read_opossum_file(filename: str) -> OpossumFileContent:
    return OpossumFileContent.from_file(file_name=filename)
