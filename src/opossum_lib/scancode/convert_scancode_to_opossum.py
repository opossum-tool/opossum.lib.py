# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0


import json
import logging
import sys
import uuid

from opossum_lib.opossum.opossum_file import (
    Metadata,
    OpossumInformation,
)
from opossum_lib.scancode.model import ScanCodeData
from opossum_lib.scancode.resource_tree import (
    convert_to_opossum_resources,
    create_attribution_mapping,
    scancode_to_file_tree,
)


def convert_scancode_to_opossum(filename: str) -> OpossumInformation:
    logging.info(f"Converting scancode to opossum {filename}")

    scancode_data = load_scancode_json(filename)
    validate_scancode_json(scancode_data, filename)

    filetree = scancode_to_file_tree(scancode_data)
    resources = convert_to_opossum_resources(filetree)
    externalAttributions, resourcesToAttributions = create_attribution_mapping(filetree)

    return OpossumInformation(
        metadata=create_opossum_metadata(scancode_data),
        resources=resources,
        externalAttributions=externalAttributions,
        resourcesToAttributions=resourcesToAttributions,
        attributionBreakpoints=[],
        externalAttributionSources={},
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


def validate_scancode_json(scancode_data: ScanCodeData, filename: str) -> None:
    if len(scancode_data.headers) != 1:
        logging.error(f"Headers of ScanCode file are invalid. File: {filename}")
        sys.exit(1)


def create_opossum_metadata(scancode_data: ScanCodeData) -> Metadata:
    scancode_header = scancode_data.headers[0]

    metadata = {
        "projectId": str(uuid.uuid4()),
        "fileCreationDate": scancode_header.end_timestamp,
        "projectTitle": "ScanCode file",
    }

    return Metadata.model_validate(metadata)
