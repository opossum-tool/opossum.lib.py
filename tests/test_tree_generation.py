# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from datetime import datetime
from pathlib import Path
from typing import List
from unittest import TestCase

import pytest
from networkx import is_weakly_connected
from spdx.model.actor import Actor, ActorType
from spdx.model.checksum import Checksum, ChecksumAlgorithm
from spdx.model.document import CreationInfo, Document
from spdx.model.file import File
from spdx.model.package import Package
from spdx.model.relationship import Relationship, RelationshipType
from spdx.parser.parse_anything import parse_file

from opossum_lib.graph_generation import generate_graph_from_spdx
from opossum_lib.tree_generation import generate_tree_from_graph
from tests.helper_methods import _create_minimal_document


def test_different_paths_graph() -> None:
    # generate tree from a directed graph with a cycle
    document = _create_minimal_document()

    graph = generate_graph_from_spdx(document)
    tree = generate_tree_from_graph(graph)

    TestCase().assertCountEqual(
        tree.nodes(),
        [
            "SPDXRef-DOCUMENT",
            "SPDXRef-Package-A",
            "SPDXRef-Package-B",
            "SPDXRef-File",
            "SPDXRef-DOCUMENT_DESCRIBES",
            "SPDXRef-Package-A_CONTAINS",
            "SPDXRef-Package-B_CONTAINS",
            "SPDXRef-Package-B_CONTAINS_SPDXRef-File",
        ],
    )
    TestCase().assertCountEqual(
        tree.edges(),
        [
            ("SPDXRef-DOCUMENT", "SPDXRef-DOCUMENT_DESCRIBES"),
            ("SPDXRef-DOCUMENT_DESCRIBES", "SPDXRef-Package-A"),
            ("SPDXRef-DOCUMENT_DESCRIBES", "SPDXRef-Package-B"),
            ("SPDXRef-Package-A", "SPDXRef-Package-A_CONTAINS"),
            ("SPDXRef-Package-A_CONTAINS", "SPDXRef-File"),
            ("SPDXRef-Package-B", "SPDXRef-Package-B_CONTAINS"),
            ("SPDXRef-Package-B_CONTAINS", "SPDXRef-Package-B_CONTAINS_SPDXRef-File"),
        ],
    )


def test_unconnected_graph() -> None:
    # test tree creation for an unconnected graph
    document = _create_minimal_document()
    document.packages += [
        Package(
            spdx_id="SPDXRef-Package-C",
            name="Package without connection to document",
            download_location="https://download.location.com",
        )
    ]

    graph = generate_graph_from_spdx(document)
    tree = generate_tree_from_graph(graph)

    TestCase().assertCountEqual(
        tree.nodes(),
        [
            "SPDXRef-DOCUMENT",
            "SPDXRef-Package-A",
            "SPDXRef-Package-B",
            "SPDXRef-File",
            "SPDXRef-DOCUMENT_DESCRIBES",
            "SPDXRef-Package-A_CONTAINS",
            "SPDXRef-Package-B_CONTAINS",
            "SPDXRef-Package-B_CONTAINS_SPDXRef-File",
            "SPDXRef-Package-C",
        ],
    )
    TestCase().assertCountEqual(
        tree.edges(),
        [
            ("SPDXRef-DOCUMENT", "SPDXRef-DOCUMENT_DESCRIBES"),
            ("SPDXRef-DOCUMENT_DESCRIBES", "SPDXRef-Package-A"),
            ("SPDXRef-DOCUMENT_DESCRIBES", "SPDXRef-Package-B"),
            ("SPDXRef-Package-A", "SPDXRef-Package-A_CONTAINS"),
            ("SPDXRef-Package-A_CONTAINS", "SPDXRef-File"),
            ("SPDXRef-Package-B", "SPDXRef-Package-B_CONTAINS"),
            ("SPDXRef-Package-B_CONTAINS", "SPDXRef-Package-B_CONTAINS_SPDXRef-File"),
        ],
    )


def test_different_roots_graph() -> None:
    # test tree generation for a connected graph where some edges are not reachable
    # from the SPDXRef-DOCUMENT node that means the connected graph has multiple sources
    # and the result should be disconnected
    download_location = "https"
    packages = [
        Package(
            spdx_id="SPDXRef-Package-A",
            name="Package-A",
            download_location=download_location,
        ),
        Package(
            spdx_id="SPDXRef-Package-B",
            name="Package-B",
            download_location=download_location,
        ),
    ]
    checksum = Checksum(ChecksumAlgorithm.SHA1, "")
    files = [
        File(spdx_id="SPDXRef-File-A", checksums=[checksum], name="File-A"),
        File(spdx_id="SPDXRef-File-B", checksums=[checksum], name="File-B"),
    ]

    relationships = [
        Relationship("SPDXRef-Package-A", RelationshipType.CONTAINS, "SPDXRef-File-A"),
        Relationship(
            "SPDXRef-DOCUMENT", RelationshipType.DESCRIBES, "SPDXRef-Package-A"
        ),
        Relationship(
            "SPDXRef-DOCUMENT", RelationshipType.DESCRIBES, "SPDXRef-Package-B"
        ),
        Relationship("SPDXRef-File-B", RelationshipType.DESCRIBES, "SPDXRef-Package-B"),
    ]
    document = Document(
        creation_info=CreationInfo(
            spdx_id="SPDXRef-DOCUMENT",
            spdx_version="SPDX-2.3",
            name="Document",
            document_namespace="https",
            created=datetime(2022, 2, 2),
            creators=[Actor(ActorType.PERSON, "Me")],
        ),
        files=files,
        relationships=relationships,
        packages=packages,
    )

    graph = generate_graph_from_spdx(document)
    tree = generate_tree_from_graph(graph)

    TestCase().assertCountEqual(
        tree.nodes(),
        [
            "SPDXRef-DOCUMENT",
            "SPDXRef-Package-A",
            "SPDXRef-Package-B",
            "SPDXRef-File-A",
            "SPDXRef-File-B",
            "SPDXRef-DOCUMENT_DESCRIBES",
            "SPDXRef-Package-A_CONTAINS",
            "SPDXRef-File-B_DESCRIBES",
            "SPDXRef-File-B_DESCRIBES_SPDXRef-Package-B",
        ],
    )
    TestCase().assertCountEqual(
        tree.edges(),
        [
            ("SPDXRef-DOCUMENT", "SPDXRef-DOCUMENT_DESCRIBES"),
            ("SPDXRef-DOCUMENT_DESCRIBES", "SPDXRef-Package-A"),
            ("SPDXRef-DOCUMENT_DESCRIBES", "SPDXRef-Package-B"),
            ("SPDXRef-Package-A", "SPDXRef-Package-A_CONTAINS"),
            ("SPDXRef-Package-A_CONTAINS", "SPDXRef-File-A"),
            ("SPDXRef-File-B", "SPDXRef-File-B_DESCRIBES"),
            ("SPDXRef-File-B_DESCRIBES", "SPDXRef-File-B_DESCRIBES_SPDXRef-Package-B"),
        ],
    )

    assert is_weakly_connected(graph)
    assert not is_weakly_connected(tree)


@pytest.mark.parametrize(
    "file_name, nodes_count, edges_count, relationship_node_keys",
    [
        (
            "SPDXJSONExample-v2.3.spdx.json",
            25,
            22,
            ["SPDXRef-Package_DYNAMIC_LINK", "SPDXRef-JenaLib_CONTAINS"],
        ),
        ("SPDX.spdx", 12, 10, []),
    ],
)
def test_tree_generation_for_bigger_examples(
    file_name: str,
    nodes_count: int,
    edges_count: int,
    relationship_node_keys: List[str],
) -> None:
    document = parse_file(str(Path(__file__).resolve().parent / "data" / file_name))
    graph = generate_graph_from_spdx(document)
    tree = generate_tree_from_graph(graph)

    assert document.creation_info.spdx_id in tree.nodes()
    assert tree.number_of_nodes() == nodes_count
    assert tree.number_of_nodes() >= graph.number_of_nodes()
    assert tree.number_of_edges() == edges_count
    assert tree.number_of_edges() >= graph.number_of_edges()
