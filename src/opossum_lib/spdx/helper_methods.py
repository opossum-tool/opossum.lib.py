# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Any

from networkx import DiGraph, weakly_connected_components
from spdx_tools.spdx.constants import DOCUMENT_SPDX_ID
from spdx_tools.spdx.model import File, Package, Snippet

from ..opossum.opossum_file import ResourceType


def _get_source_for_graph_traversal(connected_subgraph: DiGraph) -> str | None:
    return (
        DOCUMENT_SPDX_ID
        if DOCUMENT_SPDX_ID in connected_subgraph.nodes
        else _get_node_without_incoming_edge(connected_subgraph)
    )


def _get_node_without_incoming_edge(graph: DiGraph) -> str | None:
    for node, degree in graph.in_degree():
        if degree == 0 and _node_represents_a_spdx_element(graph, node):
            return str(node)
    # if there is no node without incoming edge, choose the first in the list of nodes,
    # nodes are stored as a dict which keeps the order in which the nodes are added,
    return None


def _node_represents_a_spdx_element(graph: DiGraph, node: str) -> bool:
    return "element" in graph.nodes[node]


def _weakly_connected_component_sub_graphs(graph: DiGraph) -> list[DiGraph]:
    connected_sub_graphs = []
    for connected_set in weakly_connected_components(
        graph
    ):  # returns only a set of nodes without edges
        connected_sub_graphs.append(graph.subgraph(connected_set).copy())

    return connected_sub_graphs


def _create_file_path_from_graph_path(path: list[str], graph: DiGraph) -> str:
    base_path = "/" + "/".join(
        [_replace_prefix(graph.nodes[node]["label"]) for node in path]
    )
    if list(graph.successors(path[-1])):
        base_path += "/"
    return base_path


def _replace_node_ids_with_labels_and_add_resource_type(
    path: list[str], graph: DiGraph
) -> list[tuple[str, ResourceType]]:
    resulting_path = []
    path_with_label_and_resource_type = [
        (
            _replace_prefix(graph.nodes[node]["label"]),
            _get_resource_type(graph.nodes[node]),
        )
        for node in path
    ]
    for element_or_path, resource_type in path_with_label_and_resource_type:
        resulting_path.extend(
            [
                (element, resource_type)
                for element in element_or_path.split("/")
                if element
            ]
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


def _get_resource_type(node_attributes: dict[str, Any]) -> ResourceType:
    element = node_attributes.get("element")
    if isinstance(element, Package):
        return ResourceType.FOLDER
    elif isinstance(element, Snippet | File):
        return ResourceType.FILE
    else:
        return ResourceType.OTHER
