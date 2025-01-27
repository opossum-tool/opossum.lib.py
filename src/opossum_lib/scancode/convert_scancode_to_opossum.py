# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0


import json
import logging
import sys
import uuid
from pathlib import PurePath

import opossum_lib.core.opossum_model as opossum_model
from opossum_lib.opossum.opossum_file_content import OpossumFileContent
from opossum_lib.scancode.constants import SCANCODE_SOURCE_NAME
from opossum_lib.scancode.model import File, FileType, Header, ScanCodeData


def convert_scancode_file_to_opossum(filename: str) -> OpossumFileContent:
    logging.info(f"Converting scancode to opossum {filename}")

    scancode_data = load_scancode_json(filename)

    return convert_scancode_to_opossum(scancode_data).to_opossum_file_format()


def convert_scancode_to_opossum(scancode_data: ScanCodeData) -> opossum_model.Opossum:
    resources = extract_opossum_resources(scancode_data)

    scancode_header = extract_scancode_header(scancode_data)
    metadata = opossum_model.Metadata(
        project_id=str(uuid.uuid4()),
        file_creation_date=scancode_header.end_timestamp,
        project_title="ScanCode file",
    )

    return opossum_model.Opossum(
        scan_results=opossum_model.ScanResults(
            metadata=metadata,
            resources=resources,
        )
    )


def load_scancode_json(filename: str) -> ScanCodeData:
    try:
        with open(filename) as inp:
            json_data = json.load(inp)
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding json for file {filename}. Message: {e.msg}")
        sys.exit(1)
    except UnicodeDecodeError:
        logging.error(f"Error decoding json for file {filename}.")
        sys.exit(1)

    scancode_data = ScanCodeData.model_validate(json_data)

    return scancode_data


def extract_scancode_header(scancode_data: ScanCodeData) -> Header:
    if len(scancode_data.headers) != 1:
        logging.error("Headers of ScanCode file are invalid.")
        sys.exit(1)
    return scancode_data.headers[0]


def extract_opossum_resources(
    scancode_data: ScanCodeData,
) -> list[opossum_model.Resource]:
    temp_root = opossum_model.Resource(path=PurePath(""))
    for file in scancode_data.files:
        resource = opossum_model.Resource(
            path=PurePath(file.path),
            attributions=get_attribution_info(file),
            type=convert_resource_type(file.type),
        )
        temp_root.add_resource(resource)

    return list(temp_root.children.values())


def convert_resource_type(file_type: FileType) -> opossum_model.ResourceType:
    if file_type == FileType.FILE:
        return opossum_model.ResourceType.FILE
    else:
        return opossum_model.ResourceType.FOLDER


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
