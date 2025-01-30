# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0


import json
import logging
import sys
from pathlib import Path
from zipfile import ZipFile

from opossum_lib.shared.constants import (
    INPUT_JSON_NAME,
    OUTPUT_JSON_NAME,
)
from opossum_lib.shared.entities.opossum_file_model import OpossumFileModel
from opossum_lib.shared.entities.opossum_input_file_model import OpossumInputFileModel
from opossum_lib.shared.entities.opossum_output_file_model import OpossumOutputFileModel


def read_opossum_file(path: Path) -> OpossumFileModel:
    logging.info(f"Converting opossum to opossum {path}")

    try:
        with (
            ZipFile(path, "r") as input_zip_file,
        ):
            _validate_zip_file_contents(input_zip_file)
            input_file = _read_input_json_from_zip_file(input_zip_file)
            return OpossumFileModel(
                input_file=input_file,
                output_file=_read_output_json_if_exists(input_zip_file),
            )
    except Exception as e:
        print(f"Error reading file {path}: {e}")
        sys.exit(1)


def _read_input_json_from_zip_file(zip_file: ZipFile) -> OpossumInputFileModel:
    with zip_file.open(INPUT_JSON_NAME) as input_json_file:
        input_json = json.load(input_json_file)
        input_file = OpossumInputFileModel.model_validate(input_json)
    return input_file


def _read_output_json_if_exists(
    input_zip_file: ZipFile,
) -> OpossumOutputFileModel | None:
    if OUTPUT_JSON_NAME in input_zip_file.namelist():
        with input_zip_file.open(OUTPUT_JSON_NAME) as output_json_file:
            output_json = json.load(output_json_file)
            output_file = OpossumOutputFileModel.model_validate(output_json)
    else:
        output_file = None
    return output_file


def _validate_zip_file_contents(input_zip_file: ZipFile) -> None:
    if INPUT_JSON_NAME not in input_zip_file.namelist():
        logging.error(
            f"Opossum file {input_zip_file.filename} is corrupt"
            f" and does not contain '{INPUT_JSON_NAME}'"
        )
        sys.exit(1)
