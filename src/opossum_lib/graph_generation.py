# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from networkx import DiGraph  # type: ignore
from spdx.model.document import Document


def generate_graph_from_spdx_lite(document: Document) -> DiGraph:
    graph = DiGraph()

    document_spdx_id = document.creation_info.spdx_id
    graph.add_node(document_spdx_id)

    graph.add_node("DESCRIBES")
    graph.add_edge(document_spdx_id, "DESCRIBES")

    package_spdx_ids = [package.spdx_id for package in document.packages]
    graph.add_nodes_from(package_spdx_ids)
    graph.add_edges_from(("DESCRIBES", spdx_id) for spdx_id in package_spdx_ids)

    return graph
