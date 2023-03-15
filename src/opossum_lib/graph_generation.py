# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Dict, List

from networkx import DiGraph  # type: ignore
from spdx.model.document import Document
from spdx.model.relationship import Relationship


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


def generate_graph_from_file(document: Document) -> DiGraph:
    graph = DiGraph()
    graph.add_node(document.creation_info.spdx_id, element=document.creation_info)

    relationships_by_spdx_id: Dict[
        str, List[Relationship]
    ] = get_relationships_by_spdx_id(document.relationships)

    for spdx_id in relationships_by_spdx_id.keys():
        if spdx_id not in graph.nodes():
            graph.add_node(spdx_id)
        for relationship in relationships_by_spdx_id[spdx_id]:
            relationship_node_key = (
                str(relationship.spdx_element_id)
                + "_"
                + relationship.relationship_type.name
            )
            graph.add_node(relationship_node_key, comment=relationship.comment)
            graph.add_edge(relationship.spdx_element_id, relationship_node_key)
            # if the related spdx element is SpdxNone or SpdxNoAssertion we need a
            # type conversion
            spdx_element_id = str(relationship.related_spdx_element_id)

            if spdx_element_id not in graph.nodes():
                graph.add_node(spdx_element_id)
            graph.add_edge(relationship_node_key, spdx_element_id)

    return graph


def get_relationships_by_spdx_id(
    relationships: List[Relationship],
) -> Dict[str, List[Relationship]]:
    relationships_by_spdx_id: Dict[str, List[Relationship]] = dict()
    for relationship in relationships:
        relationships_by_spdx_id.setdefault(relationship.spdx_element_id, []).append(
            relationship
        )

    return relationships_by_spdx_id
