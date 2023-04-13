# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
import json
from dataclasses import asdict
from functools import reduce
from pathlib import Path
from typing import Any, Dict, List, Tuple

from networkx import DiGraph, shortest_path
from spdx.model.document import CreationInfo
from spdx.model.file import File
from spdx.model.package import Package
from spdx.model.snippet import Snippet

from opossum_lib.attribution_generation import (
    create_document_attribution,
    create_file_attribution,
    create_package_attribution,
    create_snippet_attribution,
)
from opossum_lib.helper_methods import (
    _create_file_path_from_graph_path,
    _create_nested_dict,
    _get_source_for_graph_traversal,
    _merge_nested_dicts,
    _node_represents_a_spdx_element,
    _replace_node_ids_with_labels,
    _weakly_connected_component_sub_graphs,
)
from opossum_lib.opossum_file import (
    Metadata,
    OpossumInformation,
    OpossumPackage,
    SourceInfo,
)


def write_dict_to_file(
    opossum_information: OpossumInformation, file_path: Path
) -> None:
    with file_path.open("w") as out:
        json.dump(
            asdict(opossum_information, dict_factory=dicts_without_none), out, indent=4
        )


def dicts_without_none(x: List[Tuple[str, Any]]) -> Dict[Any, Any]:
    return {k: v for (k, v) in x if v is not None}


def generate_json_file_from_tree(tree: DiGraph) -> OpossumInformation:
    metadata = create_metadata(tree)
    resources: Dict[str, Any] = dict()
    resources_to_attributions: Dict[str, List[str]] = dict()
    external_attributions: Dict[str, OpossumPackage] = dict()
    attribution_breakpoints = []

    external_attributions["file-identifier"] = OpossumPackage(
        source=SourceInfo("File", 0)
    )
    external_attributions["package-identifier"] = OpossumPackage(
        source=SourceInfo("Package", 0)
    )
    external_attributions["snippet-identifier"] = OpossumPackage(
        source=SourceInfo("Snippet", 0)
    )

    for connected_subgraph in _weakly_connected_component_sub_graphs(tree):
        source = _get_source_for_graph_traversal(connected_subgraph)
        if source is None:
            raise RuntimeError(
                "A tree should always have a node without incoming edge."
            )
        resources_list = []
        for node in connected_subgraph.nodes():
            path: List[str] = shortest_path(connected_subgraph, source, node)
            path_with_labels: List[str] = _replace_node_ids_with_labels(
                path, connected_subgraph
            )
            file_path: str = _create_file_path_from_graph_path(connected_subgraph, path)

            resources_list.append(_create_nested_dict(path_with_labels))
            if _node_represents_a_spdx_element(connected_subgraph, node):
                create_attribution_and_link_with_resource(
                    external_attributions,
                    resources_to_attributions,
                    file_path,
                    node,
                    connected_subgraph,
                )

            else:
                attribution_breakpoints.append(file_path)

        resources.update(
            reduce(
                lambda dict1, dict2: _merge_nested_dicts(dict1, dict2), resources_list  # type: ignore  # noqa
            )
        )
    opossum_information = OpossumInformation(
        metadata=metadata,
        resources=resources,
        externalAttributions=external_attributions,
        resourcesToAttributions=resources_to_attributions,
        attributionBreakpoints=attribution_breakpoints,
    )
    return opossum_information


def create_attribution_and_link_with_resource(
    external_attributions: Dict[str, OpossumPackage],
    resources_to_attributions: Dict[str, List[str]],
    file_path: str,
    node: str,
    tree: DiGraph,
) -> None:
    if isinstance(tree.nodes[node]["element"], Package):
        external_attributions.update(
            create_package_attribution(tree.nodes[node]["element"])
        )
        resources_to_attributions[file_path] = [
            tree.nodes[node]["element"].spdx_id,
            "package-identifier",
        ]
    elif isinstance(tree.nodes[node]["element"], File):
        external_attributions.update(
            create_file_attribution(tree.nodes[node]["element"])
        )
        resources_to_attributions[file_path] = [
            tree.nodes[node]["element"].spdx_id,
            "file-identifier",
        ]
    elif isinstance(tree.nodes[node]["element"], Snippet):
        external_attributions.update(
            create_snippet_attribution(tree.nodes[node]["element"])
        )
        resources_to_attributions[file_path] = [
            tree.nodes[node]["element"].spdx_id,
            "snippet-identifier",
        ]
    elif isinstance(tree.nodes[node]["element"], CreationInfo):
        external_attributions.update(
            create_document_attribution(tree.nodes[node]["element"])
        )
        resources_to_attributions[file_path] = [tree.nodes[node]["element"].spdx_id]

    else:
        external_attributions[node] = OpossumPackage(
            source=SourceInfo(tree.nodes[node]["label"], 50)
        )
        resources_to_attributions[file_path] = [node]


def create_metadata(tree: DiGraph) -> Metadata:
    doc_name = tree.nodes["SPDXRef-DOCUMENT"]["element"].name
    created = tree.nodes["SPDXRef-DOCUMENT"]["element"].created
    metadata = Metadata("tools-python-opossum-crossover", created.isoformat(), doc_name)
    return metadata
