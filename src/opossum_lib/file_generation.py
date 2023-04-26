# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
import json
from dataclasses import fields
from pathlib import Path
from typing import Dict, List, Union

from networkx import DiGraph, shortest_path
from spdx_tools.spdx.model.document import CreationInfo
from spdx_tools.spdx.model.file import File
from spdx_tools.spdx.model.package import Package
from spdx_tools.spdx.model.snippet import Snippet

from opossum_lib.attribution_generation import (
    create_document_attribution,
    create_file_attribution,
    create_package_attribution,
    create_snippet_attribution,
)
from opossum_lib.helper_methods import (
    _create_file_path_from_graph_path,
    _get_source_for_graph_traversal,
    _node_represents_a_spdx_element,
    _replace_node_ids_with_labels,
    _weakly_connected_component_sub_graphs,
)
from opossum_lib.opossum_file import (
    Metadata,
    OpossumInformation,
    OpossumPackage,
    OpossumPackageIdentifier,
    Resource,
    SourceInfo,
)


def write_dict_to_file(
    opossum_information: OpossumInformation, file_path: Path
) -> None:
    with file_path.open("w") as out:
        json.dump(to_dict(opossum_information), out, indent=4)


def to_dict(
    element: Union[
        Resource,
        Metadata,
        OpossumPackage,
        OpossumInformation,
        SourceInfo,
        str,
        int,
        bool,
        Dict[str, OpossumPackage],
        Dict[str, List[str]],
        List[str],
        None,
    ]
) -> Union[Dict, str, List[str], bool, int, None]:
    if isinstance(element, Resource):
        return element.to_dict()
    if isinstance(element, (Metadata, OpossumPackage, OpossumInformation, SourceInfo)):
        result = []
        for f in fields(element):
            value = to_dict(getattr(element, f.name))
            result.append((f.name, value))
        return {k: v for (k, v) in result if v is not None}
    elif isinstance(element, dict):
        return {k: to_dict(v) for k, v in element.items()}
    else:
        return element


def generate_json_file_from_tree(tree: DiGraph) -> OpossumInformation:
    metadata = create_metadata(tree)
    resources = Resource()
    resources_to_attributions: Dict[str, List[str]] = dict()
    external_attributions: Dict[str, OpossumPackage] = dict()
    attribution_breakpoints = []

    external_attributions["file-identifier"] = OpossumPackage(source=SourceInfo("File"))
    external_attributions["package-identifier"] = OpossumPackage(
        source=SourceInfo("Package")
    )
    external_attributions["snippet-identifier"] = OpossumPackage(
        source=SourceInfo("Snippet")
    )

    for connected_subgraph in _weakly_connected_component_sub_graphs(tree):
        source = _get_source_for_graph_traversal(connected_subgraph)
        if source is None:
            raise RuntimeError(
                "A tree should always have a node without incoming edge."
            )
        for node in connected_subgraph.nodes():
            path: List[str] = shortest_path(connected_subgraph, source, node)
            path_with_labels: List[str] = _replace_node_ids_with_labels(
                path, connected_subgraph
            )
            resources.add_path(path_with_labels)
            file_path: str = _create_file_path_from_graph_path(path, connected_subgraph)
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

    opossum_information = OpossumInformation(
        metadata=metadata,
        resources=resources,
        externalAttributions=external_attributions,
        resourcesToAttributions=resources_to_attributions,
        attributionBreakpoints=attribution_breakpoints,
    )
    return opossum_information


def create_attribution_and_link_with_resource(
    external_attributions: Dict[OpossumPackageIdentifier, OpossumPackage],
    resources_to_attributions: Dict[OpossumPackageIdentifier, List[str]],
    file_path: str,
    node: str,
    tree: DiGraph,
) -> None:
    node_element = tree.nodes[node]["element"]
    if isinstance(node_element, Package):
        external_attributions[node_element.spdx_id] = create_package_attribution(
            package=node_element
        )
        resources_to_attributions[file_path] = [
            node_element.spdx_id,
            "package-identifier",
        ]
    elif isinstance(node_element, File):
        external_attributions[node_element.spdx_id] = create_file_attribution(
            node_element
        )
        resources_to_attributions[file_path] = [
            node_element.spdx_id,
            "file-identifier",
        ]
    elif isinstance(node_element, Snippet):
        external_attributions[node_element.spdx_id] = create_snippet_attribution(
            node_element
        )
        resources_to_attributions[file_path] = [
            node_element.spdx_id,
            "snippet-identifier",
        ]
    elif isinstance(node_element, CreationInfo):
        external_attributions[node_element.spdx_id] = create_document_attribution(
            node_element
        )
        resources_to_attributions[file_path] = [node_element.spdx_id]

    else:
        external_attributions[node] = OpossumPackage(
            source=SourceInfo(tree.nodes[node]["label"])
        )
        resources_to_attributions[file_path] = [node]


def create_metadata(tree: DiGraph) -> Metadata:
    doc_name = tree.nodes["SPDXRef-DOCUMENT"]["element"].name
    created = tree.nodes["SPDXRef-DOCUMENT"]["element"].created
    metadata = Metadata("tools-python-opossum-crossover", created.isoformat(), doc_name)
    return metadata
