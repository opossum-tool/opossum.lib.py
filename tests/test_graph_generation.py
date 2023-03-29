# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
from typing import List

import pytest
from spdx.parser.parse_anything import parse_file
from spdx.validation.document_validator import validate_full_spdx_document

from opossum_lib.graph_generation import (
    generate_graph_from_spdx,
    generate_graph_from_spdx_lite,
)


def test_generate_graph_from_spdx_lite() -> None:
    document = parse_file(
        str(Path(__file__).resolve().parent / "data" / "SPDXLite.spdx")
    )
    graph = generate_graph_from_spdx_lite(document)

    assert document.creation_info.spdx_id in graph.nodes()
    assert graph.number_of_nodes() == 4
    assert "DESCRIBES" in graph.nodes()
    assert graph.number_of_edges() == 3


@pytest.mark.parametrize(
    "file_name, nodes_count, edges_count, relationship_node_keys",
    [
        (
            "SPDXJSONExample-v2.3.spdx.json",
            20,
            22,
            ["SPDXRef-Package_DYNAMIC_LINK", "SPDXRef-JenaLib_CONTAINS"],
        ),
        ("SPDX.spdx", 11, 10, []),
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
