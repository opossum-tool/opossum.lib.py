# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, TypedDict, Union

from networkx import DiGraph, shortest_path, weakly_connected_components

from opossum_lib.helper_methods import (
    _get_source_for_graph_traversal,
    _node_represents_a_spdx_element,
)

OpossumInformation = TypedDict(
    "OpossumInformation",
    {
        "metadata": Dict[str, str],
        "resources": Dict[str, Any],
        "externalAttributions": Dict,
        "resourcesToAttributions": Dict,
        "attributionBreakpoints": List[str],
    },
)


def write_dict_to_file(
    opossum_information: OpossumInformation, file_path: Path
) -> None:
    with file_path.open("w") as out:
        json.dump(opossum_information, out, indent=4)


def generate_json_file_from_tree(
    tree: DiGraph,
) -> OpossumInformation:
    doc_name = tree.nodes["SPDXRef-DOCUMENT"]["element"].name

    opossum_information: OpossumInformation = {
        "metadata": {
            "projectId": "tools-python-opossum-crossover",
            "projectTitle": doc_name,
            "fileCreationDate": datetime.datetime.utcnow().isoformat(),
        },
        "resources": {},
        "externalAttributions": {},
        "resourcesToAttributions": {},
        "attributionBreakpoints": [],
    }

    for connected_set in weakly_connected_components(tree):
        connected_subgraph = tree.subgraph(connected_set).copy()
        source = _get_source_for_graph_traversal(connected_subgraph)
        if source is None:  # from development not possible, how to deal with this?
            raise RuntimeError(
                "A tree should always have a node without incoming edge."
            )

        opossum_information["resources"][source] = tree_to_dict(
            connected_subgraph, source
        )
        opossum_information["attributionBreakpoints"].extend(
            get_breakpoints(connected_subgraph, source)
        )

    return opossum_information


def tree_to_dict(graph: DiGraph, source: str) -> Union[int, Dict[str, Any]]:
    successors = list(graph.successors(source))
    if not successors:
        return 1
    branch_dict = {}
    for successor in successors:
        successor_name = graph.nodes[successor]["label"]
        branch_dict[successor_name] = tree_to_dict(graph, successor)
    return branch_dict


def get_breakpoints(graph: DiGraph, source: str) -> List[str]:
    breakpoints = []
    for node in graph.nodes():
        if not _node_represents_a_spdx_element(graph, node):
            path = shortest_path(graph, source, node)
            breakpoints.append(_create_file_path_from_graph_path(graph, path))

    return breakpoints


def _create_file_path_from_graph_path(graph: DiGraph, path: List[str]) -> str:
    return "/" + "/".join([graph.nodes[node]["label"] for node in path]) + "/"
