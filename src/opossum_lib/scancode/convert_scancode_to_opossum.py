# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0


import json
import logging
import sys
import uuid
from typing import Any

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
            jsondata = json.load(inp)
    except json.JSONDecodeError as jsde:
        logging.error(f"Error decoding json for file {filename}. Message: {jsde.msg}")
        sys.exit(1)
    except UnicodeDecodeError:
        logging.error(f"Error decoding json for file {filename}.")
        sys.exit(1)

    return OpossumInformation(
        metadata=create_opossum_metadata(jsondata),
        resources=Resource(type=ResourceType.FILE, children={}),
        externalAttributions={},
        resourcesToAttributions={},
        attributionBreakpoints=[],
        externalAttributionSources={},
    )


def create_opossum_metadata(json_data: Any) -> Metadata:
    header_data = json_data["headers"]
    assert len(header_data) == 1
    header = header_data[0]
    projectId = str(uuid.uuid4())
    fileCreationDate = header["end_timestamp"]
    projectTitle = "ScanCode file"

    return Metadata(projectId, fileCreationDate, projectTitle)
