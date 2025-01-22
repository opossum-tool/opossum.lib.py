# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

import pytest
from networkx import DiGraph

from opossum_lib.spdx.helper_methods import (
    _create_file_path_from_graph_path,
)


@pytest.mark.parametrize(
    "node_label", ["node/with/path", "./node/with/path", "/node/with/path"]
)
def test_create_file_path_from_graph_path(node_label: str) -> None:
    graph = _create_simple_graph(node_label)
    path = ["root", "node", "leaf"]

    file_path = _create_file_path_from_graph_path(path, graph)

    assert file_path == "root/node/with/path/leaf"


def _create_simple_graph(node_label: str) -> DiGraph:
    graph = DiGraph()
    graph.add_nodes_from(
        [
            ("root", {"label": "root"}),
            ("node", {"label": node_label}),
            ("leaf", {"label": "leaf"}),
        ]
    )
    return graph
