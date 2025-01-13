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
    Resource,
    ResourceType,
)


def convert_scancode_to_opossum(filename: str) -> OpossumInformation:
    logging.info(f"Converting scancode to opossum {filename}")

    try:
        with open(filename) as inp:
            json_data = json.load(inp)
    except json.JSONDecodeError as jsde:
        logging.error(f"Error decoding json for file {filename}. Message: {jsde.msg}")
        sys.exit(1)
    except UnicodeDecodeError:
        logging.error(f"Error decoding json for file {filename}.")
        sys.exit(1)

    scanCodeData = ScanCodeData.model_validate(json_data)

    return OpossumInformation(
        metadata=create_opossum_metadata(scanCodeData),
        resources=Resource(type=ResourceType.FILE, children={}),
        externalAttributions={},
        resourcesToAttributions={},
        attributionBreakpoints=[],
        externalAttributionSources={},
    )


def create_opossum_metadata(scancode_data: ScanCodeData) -> Metadata:
    if len(scancode_data.headers) == 0:
        logging.error("ScanCode data is missing the header!")
        sys.exit(1)
    elif len(scancode_data.headers) > 1:
        logging.error(f"ScanCode data has {len(scancode_data.headers)} headers!")
        sys.exit(1)

    the_header = scancode_data.headers[0]

    projectId = str(uuid.uuid4())
    fileCreationDate = the_header.end_timestamp
    projectTitle = "ScanCode file"

    return Metadata(projectId, fileCreationDate, projectTitle)
