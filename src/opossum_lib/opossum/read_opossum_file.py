# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
import logging
from datetime import datetime

from opossum_lib.opossum.opossum_file import (
    Metadata,
    OpossumInformation,
    Resource,
    ResourceType,
)


def read_opossum_file(filename: str) -> OpossumInformation:
    logging.info(f"Converting opossum to opossum {filename}")
    dummy_metadata = Metadata(
        projectId="test id",
        fileCreationDate=datetime.now().isoformat(),
        projectTitle="test title",
    )
    return OpossumInformation(
        metadata=dummy_metadata,
        resources=Resource(type=ResourceType.FILE, children={}),
        externalAttributions={},
        resourcesToAttributions={},
        attributionBreakpoints=[],
        externalAttributionSources={},
    )
