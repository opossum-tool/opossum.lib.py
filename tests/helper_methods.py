# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from datetime import datetime

from spdx.model.actor import Actor, ActorType
from spdx.model.checksum import Checksum, ChecksumAlgorithm
from spdx.model.document import CreationInfo, Document
from spdx.model.file import File
from spdx.model.package import Package
from spdx.model.relationship import Relationship, RelationshipType


def _create_minimal_document() -> Document:
    # this is a helper method to create a minimal document that describes two
    # packages which both contain the same file
    creation_info = CreationInfo(
        spdx_version="SPDX-2.3",
        spdx_id="SPDXRef-DOCUMENT",
        data_license="CC0-1.0",
        name="SPDX Lite Document",
        document_namespace="https://test.namespace.com",
        creators=[Actor(ActorType.PERSON, "Meret Behrens")],
        created=datetime(2023, 3, 14, 8, 49),
    )
    package_a = Package(
        name="Example package A",
        spdx_id="SPDXRef-Package-A",
        download_location="https://download.com",
    )
    package_b = Package(
        name="Example package B",
        spdx_id="SPDXRef-Package-B",
        download_location="https://download.com",
    )
    file = File(
        name="Example file",
        spdx_id="SPDXRef-File",
        checksums=[Checksum(ChecksumAlgorithm.SHA1, "")],
    )

    relationships = [
        Relationship(
            "SPDXRef-DOCUMENT", RelationshipType.DESCRIBES, "SPDXRef-Package-A"
        ),
        Relationship(
            "SPDXRef-DOCUMENT", RelationshipType.DESCRIBES, "SPDXRef-Package-B"
        ),
        Relationship("SPDXRef-Package-A", RelationshipType.CONTAINS, "SPDXRef-File"),
        Relationship("SPDXRef-Package-B", RelationshipType.CONTAINS, "SPDXRef-File"),
    ]
    document = Document(
        creation_info=creation_info,
        packages=[package_a, package_b],
        files=[file],
        relationships=relationships,
    )

    return document
