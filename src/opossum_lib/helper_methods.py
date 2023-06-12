# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from typing import List, Optional

from networkx import DiGraph, weakly_connected_components
from spdx_tools.spdx.constants import DOCUMENT_SPDX_ID


def _get_source_for_graph_traversal(connected_subgraph: DiGraph) -> Optional[str]:
    return (
        DOCUMENT_SPDX_ID
        if DOCUMENT_SPDX_ID in connected_subgraph.nodes
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


def _weakly_connected_component_sub_graphs(graph: DiGraph) -> List[DiGraph]:
    connected_sub_graphs = []
    for connected_set in weakly_connected_components(
        graph
    ):  # returns only a set of nodes without edges
        connected_sub_graphs.append(graph.subgraph(connected_set).copy())

    return connected_sub_graphs


def _create_file_path_from_graph_path(path: List[str], graph: DiGraph) -> str:
    base_path = "/" + "/".join(
        [_replace_prefix(graph.nodes[node]["label"]) for node in path]
    )
    if list(graph.successors(path[-1])):
        base_path += "/"
    return base_path


def _replace_node_ids_with_labels(path: List[str], graph: DiGraph) -> List[str]:
    resulting_path = []
    path_with_label = [_replace_prefix(graph.nodes[node]["label"]) for node in path]
    for element_or_path in path_with_label:
        resulting_path.extend(
            [element for element in element_or_path.split("/") if element]
        )

    return resulting_path


def _replace_prefix(label: str) -> str:
    """
    Some spdx element names start with "./" or "/", to avoid paths like "/./" or
    "//" we need to remove these prefixes.
    """
    if label.startswith("./"):
        return label[2:]
    elif label.startswith("/"):
        return label[1:]
    return label


def is_leaf_element(child_elements: List[str]) -> bool:
    return len(child_elements) == 0
