# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

from pathlib import Path

import opossum_lib.opossum_model as opossum_model
from opossum_lib.scancode.constants import SCANCODE_SOURCE_NAME
from opossum_lib.scancode.model import File, FileType, ScanCodeData


def scancode_to_file_tree(scancode_data: ScanCodeData) -> opossum_model.Resource:
    temp_root = opossum_model.Resource(path=Path(""))
    for file in scancode_data.files:
        resource = opossum_model.Resource(
            path=Path(file.path),
            attributions=get_attribution_info(file),
            type=convert_resource_type(file.type),
        )
        temp_root.add_resource(resource)

    assert len(temp_root.children) == 1
    return list(temp_root.children.values())[0]


def get_attribution_info(file: File) -> list[opossum_model.OpossumPackage]:
    if file.type == FileType.DIRECTORY:
        return []
    copyright = "\n".join(c.copyright for c in file.copyrights)
    source_info = opossum_model.SourceInfo(name=SCANCODE_SOURCE_NAME)

    attribution_infos = []
    for license_detection in file.license_detections:
        license_name = license_detection.license_expression_spdx
        max_score = max(m.score for m in license_detection.matches)
        attribution_confidence = int(max_score)

        package = opossum_model.OpossumPackage(
            source=source_info,
            license_name=license_name,
            attribution_confidence=attribution_confidence,
            copyright=copyright,
        )
        attribution_infos.append(package)

    return attribution_infos


def convert_resource_type(val: FileType) -> opossum_model.ResourceType:
    if val == FileType.FILE:
        return opossum_model.ResourceType.FILE
    else:
        return opossum_model.ResourceType.FOLDER
