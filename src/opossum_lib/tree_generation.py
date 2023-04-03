# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Any, Dict, Optional, Tuple, Union

from networkx import DiGraph, edge_bfs, is_weakly_connected, weakly_connected_components
from spdx.model.document import CreationInfo
from spdx.model.file import File
from spdx.model.package import Package


def generate_tree_from_graph(
    graph: DiGraph,
    source: Optional[str] = "SPDXRef-DOCUMENT",
    tree: Optional[DiGraph] = None,
) -> DiGraph:
    if not graph.edges():
        return graph

    if is_weakly_connected(graph):
        tree = tree or DiGraph()
        edges_bfs = edge_bfs(graph, source)
        visited_edges = []
        for edge in edges_bfs:
            _add_source_node(edge, graph, tree)
            _add_target_node_and_edge(edge, graph, tree)
            visited_edges += [edge]
        # check if there is a directed path from source to each element node
        # if not, we need to construct sub-graphs from the unreached edges
        # and construct trees for all of these sub-graphs, the result
        # will be an unconnected graph
        unreached_edges = set(graph.edges).difference(set(visited_edges))
        if unreached_edges:
            induced_subgraph = graph.edge_subgraph(unreached_edges)
            source = _get_node_without_incoming_edge(induced_subgraph)
            tree_component = generate_tree_from_graph(induced_subgraph, source, tree)
            tree.add_nodes_from(tree_component.nodes(data=True))
            tree.add_edges_from(tree_component.edges(data=True))

    else:  # get connected components
        tree = DiGraph()
        for connected_set in weakly_connected_components(
            graph
        ):  # returns only a set of nodes without edges
            connected_subgraph = graph.subgraph(connected_set).copy()
            # if the documents node is not in the subgraph we choose
            # any elements node without incoming edge
            source = (
                "SPDXRef-DOCUMENT"
                if "SPDXRef-DOCUMENT" in connected_set
                else _get_node_without_incoming_edge(connected_subgraph)
            )
            tree_component = generate_tree_from_graph(connected_subgraph, source)
            tree.add_nodes_from(tree_component.nodes(data=True))
            tree.add_edges_from(tree_component.edges(data=True))

    return tree


def _add_target_node_and_edge(
    edge: Tuple[str, str], graph: DiGraph, tree: DiGraph
) -> None:
    if edge[1] not in tree:
        target_node_data = graph.nodes[edge[1]]
        tree.add_node(edge[1], **target_node_data)
        tree.add_edge(*edge)
    else:
        # if the child node is already in the graph duplicate the node by adding the
        # parent node as prefix
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


def _get_node_without_incoming_edge(graph: DiGraph) -> Any:
    for node, degree in graph.in_degree():
        if degree == 0 and "element" in graph.nodes[node]:
            return node
    return ""
