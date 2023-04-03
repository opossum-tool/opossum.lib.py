# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
import datetime
import json
from typing import Any, Dict, Union

from networkx import DiGraph, weakly_connected_components

from opossum_lib.helper_methods import _get_source_for_graph_traversal


def write_dict_to_file(opossum_information: Dict, file_path: str) -> None:
    with open(file_path, "w") as out:
        json.dump(opossum_information, out, indent=4)


def generate_json_file_from_tree(tree: DiGraph) -> Dict[str, Dict[str, Any]]:
    doc_name = tree.nodes["SPDXRef-DOCUMENT"]["element"].name
    opossum_information: Dict[str, Dict[str, Any]] = {
        "metadata": {
            "projectId": "tools-python-opossum-crossover",
            "projectTitle": doc_name,
            "fileCreationDate": datetime.datetime.utcnow().isoformat(),
        },
        "resources": {},
        "externalAttributions": {},
        "resourcesToAttributions": {},
    }

    for connected_set in weakly_connected_components(tree):
        connected_subgraph = tree.subgraph(connected_set).copy()
        source = _get_source_for_graph_traversal(connected_subgraph)

        opossum_information["resources"][source] = tree_to_dict(
            connected_subgraph, source
        )

    return opossum_information


def tree_to_dict(graph: DiGraph, node: str) -> Union[int, Dict[str, Any]]:
    successors = [successor for successor in graph.successors(node)]
    if not successors:
        branch_dict: Union[int, Dict] = 1
        return branch_dict
    branch_dict = {}
    for successor in successors:
        successor_name = strip_node(successor, graph)
        branch_dict[successor_name] = tree_to_dict(graph, successor)
    return branch_dict


def strip_node(node: str, graph: DiGraph) -> str:
    # We want to revert the string concatenation for unique nodes to
    # only have the spdx_ids and RelationshipTypes as resources
    # duplicated element nodes were concatenated with the relationship,
    # the spdx_id of the element is after the last "_"
    # nodes representing RelationshipTypes were concatenated with the source node,
    # the required part is after the first "_"
    if "element" in graph.nodes[node]:
        return node.split("_")[-1]
    else:
        return node.split("_", 1)[-1]
