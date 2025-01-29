# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from zipfile import ZipFile

from opossum_lib.core.services.opossum_file_writer import OpossumFileWriter
from opossum_lib.shared.constants import (
    INPUT_JSON_NAME,
    OUTPUT_JSON_NAME,
)
from opossum_lib.shared.entities.opossum_file_model import OpossumFileModel
from tests.setup.opossum_file_faker_setup import OpossumFileFaker


def test_only_input_information_available_writes_only_input_information(
    tmp_path: Path, opossum_file_faker: OpossumFileFaker
) -> None:
    opossum_file_content = OpossumFileModel(
        input_file=opossum_file_faker.opossum_file_information()
    )
    output_path = tmp_path / "output.opossum"

    OpossumFileWriter.write(opossum_file_content, output_path)

    with ZipFile(output_path, "r") as zip_file:
        assert zip_file.namelist() == [INPUT_JSON_NAME]


def test_input_and_output_information_available_writes_both(
    tmp_path: Path, opossum_file_faker: OpossumFileFaker
) -> None:
    opossum_file_content = opossum_file_faker.opossum_file_content()
    output_path = tmp_path / "output.opossum"

    OpossumFileWriter.write(opossum_file_content, output_path)

    with ZipFile(output_path, "r") as zip_file:
        assert INPUT_JSON_NAME in zip_file.namelist()
        assert OUTPUT_JSON_NAME in zip_file.namelist()
