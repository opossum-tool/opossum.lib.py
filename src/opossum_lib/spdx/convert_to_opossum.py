# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
import sys
import uuid

from networkx import DiGraph, shortest_path
from spdx_tools.spdx.model.document import CreationInfo
from spdx_tools.spdx.model.document import Document as SpdxDocument
from spdx_tools.spdx.model.file import File
from spdx_tools.spdx.model.package import Package
from spdx_tools.spdx.model.snippet import Snippet
from spdx_tools.spdx.parser.error import SPDXParsingError
from spdx_tools.spdx.parser.parse_anything import parse_file
from spdx_tools.spdx.validation.document_validator import validate_full_spdx_document

from opossum_lib.opossum.opossum_file import (
    ExternalAttributionSource,
    Metadata,
    OpossumInformation,
    OpossumPackage,
    OpossumPackageIdentifier,
    Resource,
    ResourceType,
    SourceInfo,
)
from opossum_lib.spdx.attribution_generation import (
    create_document_attribution,
    create_file_attribution,
    create_package_attribution,
    create_snippet_attribution,
)
from opossum_lib.spdx.constants import (
    SPDX_FILE_IDENTIFIER,
    SPDX_PACKAGE_IDENTIFIER,
    SPDX_SNIPPET_IDENTIFIER,
)
from opossum_lib.spdx.graph_generation import generate_graph_from_spdx
from opossum_lib.spdx.helper_methods import (
    _create_file_path_from_graph_path,
    _get_source_for_graph_traversal,
    _node_represents_a_spdx_element,
    _replace_node_ids_with_labels_and_add_resource_type,
    _weakly_connected_component_sub_graphs,
)
from opossum_lib.spdx.tree_generation import generate_tree_from_graph


def convert_spdx_to_opossum_information(filename: str) -> OpossumInformation:
    logging.info(f"Converting {filename} to opossum information.")
    try:
        document: SpdxDocument = parse_file(filename)

    except SPDXParsingError as err:
        log_string = "\n".join(
            ["There have been issues while parsing the provided document:"]
            + [message for message in err.get_messages()]
        )
        logging.error(log_string)
        sys.exit(1)
    validation_messages = validate_full_spdx_document(document)
    if validation_messages:
        logging.warning(
            "The given SPDX document is not valid, this might cause "
            "issues with the conversion."
        )
    graph = generate_graph_from_spdx(document)
    tree = generate_tree_from_graph(graph)
    opossum_information = convert_tree_to_opossum_information(tree)
    return opossum_information


def convert_tree_to_opossum_information(tree: DiGraph) -> OpossumInformation:
    metadata = create_metadata(tree)
    resources = Resource(type=ResourceType.TOP_LEVEL)
    resources_to_attributions: dict[str, list[str]] = dict()
    external_attributions: dict[str, OpossumPackage] = dict()
    attribution_breakpoints = []
    external_attribution_sources = {
        SPDX_FILE_IDENTIFIER: ExternalAttributionSource(SPDX_FILE_IDENTIFIER, 500),
        SPDX_PACKAGE_IDENTIFIER: ExternalAttributionSource(
            SPDX_PACKAGE_IDENTIFIER, 500
        ),
        SPDX_SNIPPET_IDENTIFIER: ExternalAttributionSource(
            SPDX_SNIPPET_IDENTIFIER, 500
        ),
    }

    for connected_subgraph in _weakly_connected_component_sub_graphs(tree):
        source = _get_source_for_graph_traversal(connected_subgraph)
        if source is None:
            raise RuntimeError(
                "A tree should always have a node without incoming edge."
            )
        for node in connected_subgraph.nodes():
            path: list[str] = shortest_path(connected_subgraph, source, node)
            path_with_labels: list[tuple[str, ResourceType]] = (
                _replace_node_ids_with_labels_and_add_resource_type(
                    path, connected_subgraph
                )
            )
            resources = resources.add_path(path_with_labels)
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
        externalAttributionSources=external_attribution_sources,
    )
    return opossum_information


def create_attribution_and_link_with_resource(
    external_attributions: dict[OpossumPackageIdentifier, OpossumPackage],
    resources_to_attributions: dict[OpossumPackageIdentifier, list[str]],
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
        ]
    elif isinstance(node_element, File):
        external_attributions[node_element.spdx_id] = create_file_attribution(
            node_element
        )
        resources_to_attributions[file_path] = [
            node_element.spdx_id,
        ]
    elif isinstance(node_element, Snippet):
        external_attributions[node_element.spdx_id] = create_snippet_attribution(
            node_element
        )
        resources_to_attributions[file_path] = [
            node_element.spdx_id,
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
    metadata = Metadata(str(uuid.uuid4()), created.isoformat(), doc_name)
    return metadata
