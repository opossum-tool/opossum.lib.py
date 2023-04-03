# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from networkx import DiGraph


def _get_source_for_graph_traversal(connected_subgraph: DiGraph) -> str:
    return (
        "SPDXRef-DOCUMENT"
        if "SPDXRef-DOCUMENT" in connected_subgraph.nodes
        else _get_node_without_incoming_edge(connected_subgraph)
    )


def _get_node_without_incoming_edge(graph: DiGraph) -> str:
    for node, degree in graph.in_degree:
        if degree == 0 and "element" in graph.nodes[node]:
            return str(node)
    return ""
