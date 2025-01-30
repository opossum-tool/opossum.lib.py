# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

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
        zip_file.writestr(
            OUTPUT_JSON_NAME,
            opossum_file_model.output_file.model_dump_json(
                exclude_none=True, indent=4, by_alias=True
            ),
        )


def _write_input_json(opossum_file_model: OpossumFileModel, zip_file: ZipFile) -> None:
    zip_file.writestr(
        INPUT_JSON_NAME,
        opossum_file_model.input_file.model_dump_json(
            indent=4,
            exclude_none=True,
            by_alias=True,
        ),
    )


def _ensure_outfile_suffix(outfile_path: Path) -> Path:
    return outfile_path.with_suffix(".opossum")
