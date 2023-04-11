# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Optional

from networkx import DiGraph


def _get_source_for_graph_traversal(connected_subgraph: DiGraph) -> Optional[str]:
    return (
        "SPDXRef-DOCUMENT"
        if "SPDXRef-DOCUMENT" in connected_subgraph.nodes
        else _get_node_without_incoming_edge(connected_subgraph)
    )


def _get_node_without_incoming_edge(graph: DiGraph) -> Optional[str]:
    for node, degree in graph.in_degree():
        if degree == 0 and _node_represents_a_spdx_element(graph, node):
            return str(node)
    # if there is no node without incoming edge, choose the first in the list of nodes,
    # nodes are stored as a dict which keeps the order in which the nodes are added,
    return None


def _node_represents_a_spdx_element(graph: DiGraph, node: str) -> bool:
    return "element" in graph.nodes[node]
