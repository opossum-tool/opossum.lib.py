# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
import logging
import sys
from datetime import datetime
from zipfile import ZipFile

from opossum_lib.opossum.opossum_file import (
    Metadata,
    OpossumInformation,
    Resource,
    ResourceType,
)


def read_opossum_file(filename: str) -> OpossumInformation:
    logging.info(f"Converting opossum to opossum {filename}")

    try:
        with (
            ZipFile(filename, "r") as input_zip_file,
        ):
            if "input.json" not in input_zip_file.namelist():
                logging.error(
                    f"Opossum file {filename} is corrupt"
                    f" and does not contain 'input.json'"
                )
                sys.exit(1)
            if "output.json" in input_zip_file.namelist():
                logging.error(
                    f"Opossum file {filename} also contains"
                    f" 'output.json' which cannot be processed"
                )
                sys.exit(1)


    except Exception as e:
        # handle the exception
        print(f"Error reading file {filename}: {e}")

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
