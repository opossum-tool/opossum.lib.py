# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import sys
from zipfile import ZipFile

from pydantic import TypeAdapter

from opossum_lib.opossum.constants import INPUT_JSON_NAME, OUTPUT_JSON_NAME
from opossum_lib.opossum.opossum_file import (
    OpossumInformation,
)
from opossum_lib.opossum.opossum_file_content import OpossumFileContent
from opossum_lib.opossum.output_model import OpossumOutputFile


def read_opossum_file(filename: str) -> OpossumFileContent:
    logging.info(f"Converting opossum to opossum {filename}")

    try:
        with (
            ZipFile(filename, "r") as input_zip_file,
        ):
            validate_zip_file_contents(input_zip_file)
            input_file = read_input_json_from_zip_file(input_zip_file)
            return OpossumFileContent(
                input_file=input_file,
                output_file=read_output_json_if_exists(input_zip_file),
            )
    except Exception as e:
        print(f"Error reading file {filename}: {e}")
        sys.exit(1)


def read_input_json_from_zip_file(input_zip_file: ZipFile) -> OpossumInformation:
    with input_zip_file.open(INPUT_JSON_NAME) as input_json_file:
        input_json = json.load(input_json_file)
        input_file = TypeAdapter(OpossumInformation).validate_python(input_json)
    return input_file


def read_output_json_if_exists(input_zip_file: ZipFile) -> OpossumOutputFile | None:
    if OUTPUT_JSON_NAME in input_zip_file.namelist():
        with input_zip_file.open(OUTPUT_JSON_NAME) as output_json_file:
            output_json = json.load(output_json_file)
            output_file = TypeAdapter(OpossumOutputFile).validate_python(output_json)
    else:
        output_file = None
    return output_file


def validate_zip_file_contents(input_zip_file: ZipFile) -> None:
    if INPUT_JSON_NAME not in input_zip_file.namelist():
        logging.error(
            f"Opossum file {input_zip_file.filename} is corrupt"
            f" and does not contain '{INPUT_JSON_NAME}'"
        )
        sys.exit(1)
