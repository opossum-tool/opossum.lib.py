# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import sys
from zipfile import ZipFile

from pydantic import TypeAdapter

from opossum_lib.opossum.opossum_file import (
    OpossumInformation,
)


def read_opossum_file(filename: str) -> OpossumInformation:
    logging.info(f"Converting opossum to opossum {filename}")

    try:
        with (
            ZipFile(filename, "r") as input_zip_file,
        ):
            validate_zip_file_contents(input_zip_file)
            with input_zip_file.open("input.json") as input_json_file:
                input_json = json.load(input_json_file)
                return TypeAdapter(OpossumInformation).validate_python(input_json)
    except Exception as e:
        # handle the exception
        print(f"Error reading file {filename}: {e}")
        sys.exit(1)


def validate_zip_file_contents(input_zip_file: ZipFile) -> None:
    if "input.json" not in input_zip_file.namelist():
        logging.error(
            f"Opossum file {input_zip_file.filename} is corrupt"
            f" and does not contain 'input.json'"
        )
        sys.exit(1)
    if "output.json" in input_zip_file.namelist():
        logging.error(
            f"Opossum file {input_zip_file.filename} also contains"
            f" 'output.json' which cannot be processed"
        )
        sys.exit(1)
