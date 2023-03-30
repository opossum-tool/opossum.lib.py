# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from datetime import datetime
from pathlib import Path
from typing import List
from unittest import TestCase

import pytest
from spdx.model.actor import Actor, ActorType
from spdx.model.checksum import Checksum, ChecksumAlgorithm
from spdx.model.document import CreationInfo, Document
from spdx.model.file import File
from spdx.model.package import Package
from spdx.model.relationship import Relationship, RelationshipType
from spdx.parser.parse_anything import parse_file
from spdx.validation.document_validator import validate_full_spdx_document

from opossum_lib.graph_generation import generate_graph_from_spdx


@pytest.mark.parametrize(
    "file_name, nodes_count, edges_count, relationship_node_keys",
    [
        (
            "SPDXJSONExample-v2.3.spdx.json",
            22,
            22,
            ["SPDXRef-Package_DYNAMIC_LINK", "SPDXRef-JenaLib_CONTAINS"],
        ),
        ("SPDX.spdx", 12, 10, []),
    ],
)
def test_generate_graph_from_spdx(
    file_name: str,
    nodes_count: int,
    edges_count: int,
    relationship_node_keys: List[str],
) -> None:
    document = parse_file(str(Path(__file__).resolve().parent / "data" / file_name))
    validation_messages = validate_full_spdx_document(document)
    graph = generate_graph_from_spdx(document)

    assert document.creation_info.spdx_id in graph.nodes()

    assert graph.number_of_nodes() == nodes_count
    assert graph.number_of_edges() == edges_count
    assert "SPDXRef-DOCUMENT_DESCRIBES" in graph.nodes()
    for relationship_node_key in relationship_node_keys:
        assert relationship_node_key in graph.nodes()

    assert validation_messages == []


def test_complete_connected_graph() -> None:
    document = _create_minimal_document()

    graph = generate_graph_from_spdx(document)

    TestCase().assertCountEqual(
        graph.nodes(),
        [
            "SPDXRef-DOCUMENT",
            "SPDXRef-Package-A",
            "SPDXRef-Package-B",
            "SPDXRef-File",
            "SPDXRef-DOCUMENT_DESCRIBES",
            "SPDXRef-Package-A_CONTAINS",
            "SPDXRef-Package-B_CONTAINS",
        ],
    )
    TestCase().assertCountEqual(
        graph.edges(),
        [
            ("SPDXRef-DOCUMENT", "SPDXRef-DOCUMENT_DESCRIBES"),
            ("SPDXRef-DOCUMENT_DESCRIBES", "SPDXRef-Package-A"),
            ("SPDXRef-DOCUMENT_DESCRIBES", "SPDXRef-Package-B"),
            ("SPDXRef-Package-A", "SPDXRef-Package-A_CONTAINS"),
            ("SPDXRef-Package-A_CONTAINS", "SPDXRef-File"),
            ("SPDXRef-Package-B", "SPDXRef-Package-B_CONTAINS"),
            ("SPDXRef-Package-B_CONTAINS", "SPDXRef-File"),
        ],
    )


def test_complete_unconnected_graph() -> None:
    document = _create_minimal_document()
    document.packages += [
        Package(
            spdx_id="SPDXRef-Package-C",
            name="Package without connection to document",
            download_location="https://download.location.com",
        )
    ]

    graph = generate_graph_from_spdx(document)

    TestCase().assertCountEqual(
        graph.nodes(),
        [
            "SPDXRef-DOCUMENT",
            "SPDXRef-Package-A",
            "SPDXRef-Package-B",
            "SPDXRef-File",
            "SPDXRef-DOCUMENT_DESCRIBES",
            "SPDXRef-Package-A_CONTAINS",
            "SPDXRef-Package-B_CONTAINS",
            "SPDXRef-Package-C",
        ],
    )
    TestCase().assertCountEqual(
        graph.edges(),
        [
            ("SPDXRef-DOCUMENT", "SPDXRef-DOCUMENT_DESCRIBES"),
            ("SPDXRef-DOCUMENT_DESCRIBES", "SPDXRef-Package-A"),
            ("SPDXRef-DOCUMENT_DESCRIBES", "SPDXRef-Package-B"),
            ("SPDXRef-Package-A", "SPDXRef-Package-A_CONTAINS"),
            ("SPDXRef-Package-A_CONTAINS", "SPDXRef-File"),
            ("SPDXRef-Package-B", "SPDXRef-Package-B_CONTAINS"),
            ("SPDXRef-Package-B_CONTAINS", "SPDXRef-File"),
        ],
    )


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
