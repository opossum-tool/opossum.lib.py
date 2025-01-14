# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from pydantic import TypeAdapter

from opossum_lib.opossum.constants import COMPRESSION_LEVEL
from opossum_lib.opossum.opossum_file import (
    OpossumInformation,
)


def write_opossum_information_to_file(
    opossum_information: OpossumInformation, file_path: Path
) -> None:
    with ZipFile(
        file_path, "w", compression=ZIP_DEFLATED, compresslevel=COMPRESSION_LEVEL
    ) as z:
        z.writestr(
            "input.json",
            TypeAdapter(OpossumInformation).dump_json(
                opossum_information, indent=4, exclude_none=True
            ),
        )
