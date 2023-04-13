# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
import typing
from typing import Any, Dict, List, Optional, Union

from networkx import DiGraph, weakly_connected_components
from spdx.constants import DOCUMENT_SPDX_ID


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


def _create_file_path_from_graph_path(graph: DiGraph, path: List[str]) -> str:
    """
    some file names with relative paths start with "./", to avoid paths like "/./"
    we need to remove these prefixes
    """
    if list(graph.successors(path[-1])):
        return (
            "/"
            + "/".join([graph.nodes[node]["label"].replace("./", "") for node in path])
            + "/"
        )
    else:
        return "/" + "/".join(
            [graph.nodes[node]["label"].replace("./", "") for node in path]
        )


def _replace_node_ids_with_labels(
    path: List[str], connected_subgraph: DiGraph
) -> List[str]:
    resulting_path = []
    path_with_label = [
        connected_subgraph.nodes[node]["label"].replace("./", "") for node in path
    ]
    for element_or_path in path_with_label:
        resulting_path.extend(
            [element for element in element_or_path.split("/") if element]
        )

    return resulting_path


def _create_nested_dict(file_path: List[str]) -> Union[int, Dict[str, Any]]:
    if len(file_path) == 0:
        return 1
    else:
        return {file_path[0]: _create_nested_dict(file_path[1:])}


@typing.no_type_check
def _merge_nested_dicts(
    dict1: Union[Dict, int], dict2: Union[Dict, int]
) -> Dict[str, Any]:
    if isinstance(dict2, int) and isinstance(dict1, Dict):
        return dict1
    if isinstance(dict1, int) and isinstance(dict2, Dict):
        return dict2
    if isinstance(dict1, int) and isinstance(dict2, int):
        raise RuntimeError("A tree doesn't have two equivalent paths.")
    for key in dict2:
        if key not in dict1:
            dict1[key] = dict2[key]
        else:
            dict1[key] = _merge_nested_dicts(dict1[key], dict2[key])

    return dict1
