# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

import pytest
from networkx import get_node_attributes
from spdx_tools.spdx.model.package import Package
from spdx_tools.spdx.parser.parse_anything import parse_file
from spdx_tools.spdx.validation.document_validator import validate_full_spdx_document

from opossum_lib.spdx.graph_generation import generate_graph_from_spdx
from tests.helper_methods import _create_minimal_document


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
    relationship_node_keys: list[str],
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

    assert "DESCRIBES" in get_node_attributes(graph, "label").values()

    assert validation_messages == []


def test_complete_connected_graph() -> None:
    document = _create_minimal_document()

    graph = generate_graph_from_spdx(document)

    labels = get_node_attributes(graph, "label")
    assert labels == {
        "SPDXRef-DOCUMENT": "SPDX Lite Document",
        "SPDXRef-DOCUMENT_DESCRIBES": "DESCRIBES",
        "SPDXRef-File": "Example file",
        "SPDXRef-Package-A": "Example package A",
        "SPDXRef-Package-A_CONTAINS": "CONTAINS",
        "SPDXRef-Package-B": "Example package B",
        "SPDXRef-Package-B_CONTAINS": "CONTAINS",
    }


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

    labels = get_node_attributes(graph, "label")
    assert labels == {
        "SPDXRef-DOCUMENT": "SPDX Lite Document",
        "SPDXRef-DOCUMENT_DESCRIBES": "DESCRIBES",
        "SPDXRef-File": "Example file",
        "SPDXRef-Package-A": "Example package A",
        "SPDXRef-Package-A_CONTAINS": "CONTAINS",
        "SPDXRef-Package-B": "Example package B",
        "SPDXRef-Package-B_CONTAINS": "CONTAINS",
        "SPDXRef-Package-C": "Package without connection to document",
    }
