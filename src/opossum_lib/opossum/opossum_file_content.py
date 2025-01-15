# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0


from dataclasses import dataclass

from opossum_lib.opossum.opossum_file import OpossumInformation
from opossum_lib.opossum.output_model import OpossumOutputFile


@dataclass
class OpossumFileContent:
    input_file: OpossumInformation
    output_file: OpossumOutputFile | None = None
