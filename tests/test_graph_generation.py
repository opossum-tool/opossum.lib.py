# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
import os

import pytest
from spdx.parser.parse_anything import parse_file

from opossum_lib.graph_generation import (
    generate_graph_from_file,
    generate_graph_from_spdx_lite,
)


def test_generate_graph_from_spdx_lite() -> None:
    document = parse_file(
        os.path.join(os.path.dirname(__file__), "./data/SPDXLite.spdx")
    )

    graph = generate_graph_from_spdx_lite(document)

    assert document.creation_info.spdx_id in graph.nodes()
    assert graph.number_of_nodes() == 4
    assert len(graph.edges()) == 3


@pytest.mark.parametrize(
    "file_path, nodes_count, edges_count",
    [("./data/SPDXJSONExample-v2.3.spdx.json", 20, 22), ("./data/SPDX.spdx", 11, 10)],
)
def test_generate_graph_from_file(
    file_path: str, nodes_count: int, edges_count: int
) -> None:
    document = parse_file(os.path.join(os.path.dirname(__file__), file_path))
    graph = generate_graph_from_file(document)

    assert document.creation_info.spdx_id in graph.nodes()

    assert len(graph.nodes()) == nodes_count
    assert len(graph.edges()) == edges_count
