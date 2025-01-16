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
from opossum_lib.opossum.opossum_file_content import OpossumFileContent
from opossum_lib.scancode.model import Header, ScanCodeData
from opossum_lib.scancode.resource_tree import (
    convert_to_opossum_resources,
    create_attribution_mapping,
    scancode_to_file_tree,
)


def convert_scancode_to_opossum(filename: str) -> OpossumFileContent:
    logging.info(f"Converting scancode to opossum {filename}")

    scancode_data = load_scancode_json(filename)

    filetree = scancode_to_file_tree(scancode_data)
    resources = convert_to_opossum_resources(filetree)
    external_attributions, resources_to_attributions = create_attribution_mapping(
        filetree
    )

    scancode_header = extract_scancode_header(scancode_data, filename)
    metadata = Metadata(
        project_id=str(uuid.uuid4()),
        file_creation_date=scancode_header.end_timestamp,
        project_title="ScanCode file",
    )

    return OpossumFileContent(
        OpossumInformation(
            metadata=metadata,
            resources=resources,
            external_attributions=external_attributions,
            resources_to_attributions=resources_to_attributions,
            attribution_breakpoints=[],
            external_attribution_sources={},
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


def extract_scancode_header(scancode_data: ScanCodeData, filename: str) -> Header:
    if len(scancode_data.headers) != 1:
        logging.error(f"Headers of ScanCode file are invalid. File: {filename}")
        sys.exit(1)
    return scancode_data.headers[0]
