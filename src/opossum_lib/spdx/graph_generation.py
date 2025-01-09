# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

from networkx import DiGraph, set_node_attributes
from spdx_tools.spdx.graph_generation import generate_relationship_graph_from_spdx
from spdx_tools.spdx.model import File, Package, Snippet
from spdx_tools.spdx.model.document import CreationInfo, Document

from .helper_methods import _node_represents_a_spdx_element


def generate_graph_from_spdx(document: Document) -> DiGraph:
    graph = generate_relationship_graph_from_spdx(document)
    labels = {node: _create_label_for_node(graph, node) for node in graph.nodes}
    set_node_attributes(graph, labels, "label")

    return graph


def _create_label_for_node(graph: DiGraph, node: str) -> str:
    if _node_represents_a_spdx_element(graph, node):
        element_node: CreationInfo | File | Package | Snippet | None = graph.nodes[
            node
        ]["element"]
        if element_node:
            return element_node.name or element_node.spdx_id
        else:
            return node
    else:
        return node.split("_", 1)[-1]
