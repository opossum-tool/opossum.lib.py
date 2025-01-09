# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
import json
from dataclasses import fields
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from opossum_lib.opossum.constants import COMPRESSION_LEVEL
from opossum_lib.opossum.opossum_file import (
    ExternalAttributionSource,
    Metadata,
    OpossumInformation,
    OpossumPackage,
    Resource,
    SourceInfo,
)


def write_opossum_information_to_file(
    opossum_information: OpossumInformation, file_path: Path
) -> None:
    with ZipFile(
        file_path, "w", compression=ZIP_DEFLATED, compresslevel=COMPRESSION_LEVEL
    ) as z:
        z.writestr("input.json", json.dumps(to_dict(opossum_information), indent=4))


def to_dict(
    element: Resource
    | Metadata
    | OpossumPackage
    | OpossumInformation
    | SourceInfo
    | ExternalAttributionSource
    | str
    | int
    | bool
    | dict[str, OpossumPackage]
    | dict[str, list[str]]
    | list[str]
    | None,
) -> dict | str | list[str] | bool | int | None:
    if isinstance(element, Resource):
        return element.to_dict()
    if isinstance(
        element,
        Metadata
        | OpossumPackage
        | OpossumInformation
        | SourceInfo
        | ExternalAttributionSource,
    ):
        result = []
        for f in fields(element):
            value = to_dict(getattr(element, f.name))
            result.append((f.name, value))
        return {k: v for (k, v) in result if v is not None}
    elif isinstance(element, dict):
        return {k: to_dict(v) for k, v in element.items()}
    else:
        return element
