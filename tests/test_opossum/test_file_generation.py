# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from zipfile import ZipFile

import opossum_lib.opossum.output_model
from opossum_lib.opossum.constants import INPUT_JSON_NAME, OUTPUT_JSON_NAME
from opossum_lib.opossum.file_generation import write_opossum_information_to_file
from opossum_lib.opossum.opossum_file import Metadata, OpossumInformation
from opossum_lib.opossum.opossum_file_content import OpossumFileContent
from opossum_lib.opossum.output_model import OpossumOutputFile

OPOSSUM_INFILE = OpossumInformation(
    metadata=Metadata(
        projectId="project-id",
        fileCreationDate="30-05-2023",
        projectTitle="project-title",
    ),
    resources={},
    externalAttributions={},
    resourcesToAttributions={},
)

OPOSSUM_OUTFILE = OpossumOutputFile(
    metadata=opossum_lib.opossum.output_model.Metadata(
        projectId="project-id",
        fileCreationDate="30-05-2023",
        inputFileMd5Checksum="checksum",
    ),
    manualAttributions={},
    resourcesToAttributions={},
    resolvedExternalAttributions=None,
)


def test_only_input_information_available_writes_only_input_information(
    tmp_path: Path,
) -> None:
    opossum_file_content = OpossumFileContent(OPOSSUM_INFILE)
    output_path = tmp_path / "output.opossum"

    write_opossum_information_to_file(opossum_file_content, output_path)

    with ZipFile(output_path, "r") as zip_file:
        assert zip_file.namelist() == [INPUT_JSON_NAME]


def test_input_and_output_information_available_writes_both(tmp_path: Path) -> None:
    opossum_file_content = OpossumFileContent(
        input_file=OPOSSUM_INFILE, output_file=OPOSSUM_OUTFILE
    )
    output_path = tmp_path / "output.opossum"

    write_opossum_information_to_file(opossum_file_content, output_path)

    with ZipFile(output_path, "r") as zip_file:
        assert INPUT_JSON_NAME in zip_file.namelist()
        assert OUTPUT_JSON_NAME in zip_file.namelist()
