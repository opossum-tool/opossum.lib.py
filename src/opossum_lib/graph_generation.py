# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Dict, List

from networkx import DiGraph
from spdx.document_utils import get_contained_spdx_element_ids, get_element_from_spdx_id
from spdx.model.document import Document
from spdx.model.relationship import Relationship


def generate_graph_from_spdx(document: Document) -> DiGraph:
    graph = DiGraph()
    graph.add_node(
        document.creation_info.spdx_id,
        element=document.creation_info,
        label=document.creation_info.spdx_id,
    )

    contained_elements: List[str] = get_contained_spdx_element_ids(document)
    contained_element_nodes = [
        (
            spdx_id,
            {"element": get_element_from_spdx_id(document, spdx_id), "label": spdx_id},
        )
        for spdx_id in contained_elements
    ]
    graph.add_nodes_from(contained_element_nodes)

    relationships_by_spdx_id: Dict[
        str, List[Relationship]
    ] = _get_relationships_by_spdx_id(document.relationships)

    for spdx_id, relationships in relationships_by_spdx_id.items():
        if spdx_id not in graph.nodes():
            graph.add_node(
                spdx_id,
                element=get_element_from_spdx_id(document, spdx_id),
                label=spdx_id,
            )
        for relationship in relationships:
            relationship_node_key = (
                relationship.spdx_element_id + "_" + relationship.relationship_type.name
            )
            graph.add_node(
                relationship_node_key,
                comment=relationship.comment,
                label=relationship.relationship_type.name,
            )
            graph.add_edge(relationship.spdx_element_id, relationship_node_key)
            # if the related spdx element is SpdxNone or SpdxNoAssertion we need a
            # type conversion
            related_spdx_element_id = str(relationship.related_spdx_element_id)

            if related_spdx_element_id not in graph.nodes():
                graph.add_node(
                    related_spdx_element_id,
                    element=get_element_from_spdx_id(document, spdx_id),
                    label=related_spdx_element_id,
                )
            graph.add_edge(relationship_node_key, related_spdx_element_id)

    return graph


def _get_relationships_by_spdx_id(
    relationships: List[Relationship],
) -> Dict[str, List[Relationship]]:
    relationships_by_spdx_id: Dict[str, List[Relationship]] = dict()
    for relationship in relationships:
        relationships_by_spdx_id.setdefault(relationship.spdx_element_id, []).append(
            relationship
        )

    return relationships_by_spdx_id
