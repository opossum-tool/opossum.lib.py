# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from datetime import datetime
from pathlib import Path
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
from tests.helper_methods import (
    _create_minimal_document,
    _generate_document_with_from_root_node_unreachable_file,
)


def test_different_paths_graph() -> None:
    # generate tree from a directed graph with an undirected cycle
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
    document = _generate_document_with_from_root_node_unreachable_file()

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


def test_tree_generation_for_cycle() -> None:
    # generate tree from a graph with a directed cycle
    document = _create_minimal_document()
    document.relationships += [
        Relationship("SPDXRef-File", RelationshipType.CONTAINED_BY, "SPDXRef-Package-A")
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
            "SPDXRef-File_CONTAINED_BY",
            "SPDXRef-File_CONTAINED_BY_SPDXRef-Package-A",
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
            ("SPDXRef-Package-B", "SPDXRef-Package-B_CONTAINS"),
            ("SPDXRef-Package-A_CONTAINS", "SPDXRef-File"),
            ("SPDXRef-Package-B_CONTAINS", "SPDXRef-Package-B_CONTAINS_SPDXRef-File"),
            ("SPDXRef-File", "SPDXRef-File_CONTAINED_BY"),
            (
                "SPDXRef-File_CONTAINED_BY",
                "SPDXRef-File_CONTAINED_BY_SPDXRef-Package-A",
            ),
        ],
    )


def test_tree_generation_unconnected_cycle() -> None:
    # generate tree from a graph with a directed cycle that is not connected with the
    # documents root node
    creation_info = CreationInfo(
        spdx_version="SPDX-2.3",
        spdx_id="SPDXRef-DOCUMENT",
        data_license="CC0-1.0",
        name="SPDX Lite Document",
        document_namespace="https://test.namespace.com",
        creators=[Actor(ActorType.PERSON, "Meret Behrens")],
        created=datetime(2023, 3, 14, 8, 49),
    )
    package = Package(
        name="Example package",
        spdx_id="SPDXRef-Package",
        download_location="https://download.com",
    )
    file = File(
        name="Example file",
        spdx_id="SPDXRef-File",
        checksums=[Checksum(ChecksumAlgorithm.SHA1, "")],
    )

    relationships = [
        Relationship("SPDXRef-Package", RelationshipType.CONTAINS, "SPDXRef-File"),
        Relationship("SPDXRef-File", RelationshipType.CONTAINED_BY, "SPDXRef-Package"),
    ]
    document = Document(
        creation_info=creation_info,
        packages=[package],
        files=[file],
        relationships=relationships,
    )

    graph = generate_graph_from_spdx(document)
    tree = generate_tree_from_graph(graph)

    TestCase().assertCountEqual(
        tree.nodes(),
        [
            "SPDXRef-DOCUMENT",
            "SPDXRef-Package",
            "SPDXRef-File",
            "SPDXRef-Package_CONTAINS",
            "SPDXRef-Package_CONTAINS_SPDXRef-File",
            "SPDXRef-File_CONTAINED_BY",
            "SPDXRef-File_CONTAINED_BY_SPDXRef-Package",
        ],
    )
    TestCase().assertCountEqual(
        tree.edges(),
        [
            ("SPDXRef-File", "SPDXRef-File_CONTAINED_BY"),
            (
                "SPDXRef-File_CONTAINED_BY",
                "SPDXRef-File_CONTAINED_BY_SPDXRef-Package",
            ),
            ("SPDXRef-Package", "SPDXRef-Package_CONTAINS"),
            ("SPDXRef-Package_CONTAINS", "SPDXRef-Package_CONTAINS_SPDXRef-File"),
        ],
    )


@pytest.mark.parametrize(
    "file_name, nodes_count, edges_count",
    [
        ("SPDXJSONExample-v2.3.spdx.json", 25, 22),
        ("SPDX.spdx", 12, 10),
    ],
)
def test_tree_generation_for_bigger_examples(
    file_name: str, nodes_count: int, edges_count: int
) -> None:
    document = parse_file(str(Path(__file__).resolve().parent / "data" / file_name))
    graph = generate_graph_from_spdx(document)
    tree = generate_tree_from_graph(graph)

    assert document.creation_info.spdx_id in tree.nodes()
    assert tree.number_of_nodes() == nodes_count
    assert tree.number_of_nodes() >= graph.number_of_nodes()
    assert tree.number_of_edges() == edges_count
    assert tree.number_of_edges() >= graph.number_of_edges()
