# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from pydantic import BaseModel

from opossum_lib.shared.constants import (
    COMPRESSION_LEVEL,
    INPUT_JSON_NAME,
    OUTPUT_JSON_NAME,
)
from opossum_lib.shared.entities.opossum_file_model import OpossumFileModel


def write_opossum_file(opossum_file_model: OpossumFileModel, file_path: Path) -> None:
    file_path = _ensure_outfile_suffix(file_path)
    with ZipFile(
        file_path, "w", compression=ZIP_DEFLATED, compresslevel=COMPRESSION_LEVEL
    ) as zip_file:
        _write_input_json(opossum_file_model, zip_file)
        _write_output_json_if_existing(opossum_file_model, zip_file)


def _write_output_json_if_existing(
    opossum_file_model: OpossumFileModel, zip_file: ZipFile
) -> None:
    if opossum_file_model.output_file:
        _write_json_to_zip(zip_file, OUTPUT_JSON_NAME, opossum_file_model.output_file)


def _write_input_json(opossum_file_model: OpossumFileModel, zip_file: ZipFile) -> None:
    _write_json_to_zip(zip_file, INPUT_JSON_NAME, opossum_file_model.input_file)


def _write_json_to_zip(zip_file: ZipFile, sub_file_name: str, model: BaseModel) -> None:
    zip_file.writestr(
        sub_file_name,
        model.model_dump_json(
            indent=4,
            exclude_none=True,
            by_alias=True,
        ),
    )


def _ensure_outfile_suffix(outfile_path: Path) -> Path:
    return outfile_path.with_suffix(".opossum")
