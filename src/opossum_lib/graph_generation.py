# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from networkx import DiGraph
from spdx_tools.spdx.graph_generation import generate_relationship_graph_from_spdx
from spdx_tools.spdx.model.document import Document


def generate_graph_from_spdx(document: Document) -> DiGraph:
    graph = generate_relationship_graph_from_spdx(document)
    for node in graph.nodes():
        if "_" in node:
            graph.add_node(node, label=node.split("_", 1)[-1])
        else:
            graph.add_node(node, label=node)
    return graph
