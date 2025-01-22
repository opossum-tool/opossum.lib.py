# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

import logging
import sys
import uuid
from typing import Any

from networkx import DiGraph
from spdx_tools.spdx.model.document import CreationInfo
from spdx_tools.spdx.model.document import Document as SpdxDocument
from spdx_tools.spdx.model.file import File
from spdx_tools.spdx.model.package import Package
from spdx_tools.spdx.model.snippet import Snippet
from spdx_tools.spdx.parser.error import SPDXParsingError
from spdx_tools.spdx.parser.parse_anything import parse_file
from spdx_tools.spdx.validation.document_validator import validate_full_spdx_document

from opossum_lib.opossum.opossum_file_content import OpossumFileContent
from opossum_lib.opossum_model import (
    ExternalAttributionSource,
    Metadata,
    Opossum,
    OpossumPackage,
    Resource,
    ScanResults,
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
    _get_file_path,
    _get_resource_type,
    _get_source_for_graph_traversal,
    _node_represents_a_spdx_element,
    _weakly_connected_component_sub_graphs,
)
from opossum_lib.spdx.tree_generation import generate_tree_from_graph


def convert_spdx_to_opossum_information(filename: str) -> OpossumFileContent:
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
    return convert_tree_to_opossum(tree).to_opossum_file_format()


def convert_tree_to_opossum(tree: DiGraph) -> Opossum:
    metadata = create_metadata(tree)
    resources = []  # Resource(type=ResourceType.TOP_LEVEL)
    # resources_to_attributions: dict[str, list[str]] = dict()
    # external_attributions: dict[str, OpossumPackage] = dict()
    attribution_to_id: dict[OpossumPackage, str] = {}
    attribution_breakpoints = []
    external_attribution_sources = {
        SPDX_FILE_IDENTIFIER: ExternalAttributionSource(
            name=SPDX_FILE_IDENTIFIER, priority=500
        ),
        SPDX_PACKAGE_IDENTIFIER: ExternalAttributionSource(
            name=SPDX_PACKAGE_IDENTIFIER, priority=500
        ),
        SPDX_SNIPPET_IDENTIFIER: ExternalAttributionSource(
            name=SPDX_SNIPPET_IDENTIFIER, priority=500
        ),
    }

    for connected_subgraph in _weakly_connected_component_sub_graphs(tree):
        source = _get_source_for_graph_traversal(connected_subgraph)
        if source is None:
            raise RuntimeError(
                "A tree should always have a node without incoming edge."
            )
        source_file_path = _get_file_path(connected_subgraph, source, source)
        rootnode = Resource(path=source_file_path)
        resources.append(rootnode)
        for node_label in connected_subgraph.nodes():
            node = connected_subgraph.nodes[node_label]
            file_path: str = _get_file_path(connected_subgraph, source, node_label)
            new_resource = Resource(path=file_path, type=_get_resource_type(node))
            if _node_represents_a_spdx_element(connected_subgraph, node_label):
                attribution = create_attribution(node)
                attribution_to_id[attribution] = (
                    get_attribution_id(node["element"]) or node_label
                )
                new_resource.attributions.append(attribution)
            else:
                attribution_breakpoints.append("/" + file_path)
            rootnode.add_resource(new_resource)

    scan_results = ScanResults(
        metadata=metadata,
        resources=resources,
        attribution_to_id=attribution_to_id,
        attribution_breakpoints=attribution_breakpoints,
        external_attribution_sources=external_attribution_sources,
    )
    return Opossum(scan_results=scan_results)


def create_attribution(
    node: dict[str, Any],
) -> OpossumPackage:
    node_element = node["element"]
    if isinstance(node_element, Package):
        return create_package_attribution(package=node_element)
    elif isinstance(node_element, File):
        return create_file_attribution(node_element)
    elif isinstance(node_element, Snippet):
        return create_snippet_attribution(node_element)
    elif isinstance(node_element, CreationInfo):
        return create_document_attribution(node_element)
    else:
        return OpossumPackage(source=SourceInfo(name=node["label"]))


def get_attribution_id(element: Any) -> str | None:
    if isinstance(element, Package | File | Snippet | CreationInfo):
        return element.spdx_id
    return None


def create_metadata(tree: DiGraph) -> Metadata:
    doc_name = tree.nodes["SPDXRef-DOCUMENT"]["element"].name
    created = tree.nodes["SPDXRef-DOCUMENT"]["element"].created
    metadata = Metadata(
        project_id=str(uuid.uuid4()),
        file_creation_date=created.isoformat(),
        project_title=doc_name,
    )
    return metadata
