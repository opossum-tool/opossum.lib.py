# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Dict, Optional, Tuple, Union

from networkx import DiGraph, edge_bfs, is_weakly_connected
from spdx_tools.spdx.constants import DOCUMENT_SPDX_ID
from spdx_tools.spdx.model.document import CreationInfo
from spdx_tools.spdx.model.file import File
from spdx_tools.spdx.model.package import Package

from opossum_lib.helper_methods import (
    _get_source_for_graph_traversal,
    _weakly_connected_component_sub_graphs,
)


def generate_tree_from_graph(graph: DiGraph) -> DiGraph:
    return _generate_tree_from_graph_recursively(graph)


def _generate_tree_from_graph_recursively(
    graph: DiGraph,
    source: Optional[str] = DOCUMENT_SPDX_ID,
    created_tree: Optional[DiGraph] = None,
) -> DiGraph:
    if not graph.edges():
        return graph.copy()

    if is_weakly_connected(graph):
        if created_tree:
            created_tree = created_tree.copy()
        else:
            created_tree = DiGraph()
        edges_bfs = edge_bfs(graph, source)

        visited_edges = []
        for edge in edges_bfs:
            _add_edge_and_associated_nodes_to_tree(edge, created_tree, graph)
            visited_edges += [edge]
        # check if there is a directed path from source to each element node
        # if not, we need to construct sub-graphs from the unreached edges
        # and construct trees for all of these sub-graphs, the result
        # will be an unconnected graph
        unreached_edges = set(graph.edges).difference(set(visited_edges))
        if unreached_edges:
            induced_subgraph = graph.edge_subgraph(unreached_edges)
            source = _get_source_for_graph_traversal(induced_subgraph)
            tree_component = _generate_tree_from_graph_recursively(
                induced_subgraph, source, created_tree
            )
            created_tree.add_nodes_from(tree_component.nodes(data=True))
            created_tree.add_edges_from(tree_component.edges(data=True))

    else:  # get connected components
        if created_tree:
            created_tree = created_tree.copy()
        else:
            created_tree = DiGraph()
        for connected_subgraph in _weakly_connected_component_sub_graphs(graph):
            # if the documents node is not in the subgraph we choose
            # any elements node without incoming edge
            source = _get_source_for_graph_traversal(connected_subgraph)
            tree_component = _generate_tree_from_graph_recursively(
                connected_subgraph, source, created_tree
            )
            created_tree.add_nodes_from(tree_component.nodes(data=True))
            created_tree.add_edges_from(tree_component.edges(data=True))

    return created_tree


def _add_edge_and_associated_nodes_to_tree(
    edge: Tuple[str, str], created_tree: DiGraph, graph: DiGraph
) -> None:
    _add_source_node(edge, graph, created_tree)
    _add_target_node_and_edge(edge, graph, created_tree)


def _add_target_node_and_edge(
    edge: Tuple[str, str], graph: DiGraph, tree: DiGraph
) -> None:
    if edge[1] not in tree:
        target_node_data = graph.nodes[edge[1]]
        tree.add_node(edge[1], **target_node_data)
        tree.add_edge(*edge)
    else:
        # if the target node is already in the graph duplicate the node by adding the
        # source node as prefix
        target_node_data = graph.nodes[edge[1]]
        duplicated_node = edge[0] + "_" + edge[1]
        tree.add_node(duplicated_node, **target_node_data)
        tree.add_edge(edge[0], duplicated_node)


def _add_source_node(edge: Tuple[str, str], graph: DiGraph, tree: DiGraph) -> None:
    if edge[0] not in tree:
        source_node_data: Dict[str, Union[CreationInfo, Package, File]] = graph.nodes[
            edge[0]
        ]
        tree.add_node(edge[0], **source_node_data)
