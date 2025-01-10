# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
from unittest import TestCase

from spdx_tools.spdx.model import Document
from spdx_tools.spdx.model.package import Package
from spdx_tools.spdx.parser.parse_anything import parse_file

from opossum_lib.opossum.opossum_file import (
    ExternalAttributionSource,
    OpossumInformation,
)
from opossum_lib.spdx.constants import (
    SPDX_FILE_IDENTIFIER,
    SPDX_PACKAGE_IDENTIFIER,
    SPDX_SNIPPET_IDENTIFIER,
)
from opossum_lib.spdx.convert_to_opossum import convert_tree_to_opossum_information
from opossum_lib.spdx.graph_generation import generate_graph_from_spdx
from opossum_lib.spdx.tree_generation import generate_tree_from_graph
from tests.test_spdx.helper_methods import (
    _create_minimal_document,
    _generate_document_with_from_root_node_unreachable_file,
)


def test_different_paths_graph() -> None:
    """Creating a tree from a directed graph with a cycle."""
    expected_file_tree = {
        "SPDX Lite Document": {
            "DESCRIBES": {
                "Example package A": {"CONTAINS": {"Example file": 1}},
                "Example package B": {"CONTAINS": {"Example file": 1}},
            }
        }
    }
    document = _create_minimal_document()
    opossum_information = _get_opossum_information_from_document(document)

    file_tree = opossum_information.resources.to_dict()
    assert file_tree == expected_file_tree
    TestCase().assertCountEqual(
        opossum_information.attributionBreakpoints,
        [
            "/SPDX Lite Document/DESCRIBES/",
            "/SPDX Lite Document/DESCRIBES/Example package A/CONTAINS/",
            "/SPDX Lite Document/DESCRIBES/Example package B/CONTAINS/",
        ],
    )
    assert opossum_information.resourcesToAttributions == {
        "/SPDX Lite Document/": ["SPDXRef-DOCUMENT"],
        "/SPDX Lite Document/DESCRIBES/Example package A/": ["SPDXRef-Package-A"],
        "/SPDX Lite Document/DESCRIBES/Example package A/CONTAINS/Example file": [
            "SPDXRef-File"
        ],
        "/SPDX Lite Document/DESCRIBES/Example package B/": ["SPDXRef-Package-B"],
        "/SPDX Lite Document/DESCRIBES/Example package B/CONTAINS/Example file": [
            "SPDXRef-File"
        ],
    }

    TestCase().assertCountEqual(
        opossum_information.externalAttributions.keys(),
        [
            "SPDXRef-DOCUMENT",
            "SPDXRef-Package-A",
            "SPDXRef-File",
            "SPDXRef-Package-B",
        ],
    )

    assert opossum_information.externalAttributionSources == {
        SPDX_FILE_IDENTIFIER: ExternalAttributionSource(SPDX_FILE_IDENTIFIER, 500),
        SPDX_PACKAGE_IDENTIFIER: ExternalAttributionSource(
            SPDX_PACKAGE_IDENTIFIER, 500
        ),
        SPDX_SNIPPET_IDENTIFIER: ExternalAttributionSource(
            SPDX_SNIPPET_IDENTIFIER, 500
        ),
    }


def test_unconnected_paths_graph() -> None:
    """Creating a tree from a directed graph with a cycle."""
    expected_file_tree = {
        "SPDX Lite Document": {
            "DESCRIBES": {
                "Example package A": {"CONTAINS": {"Example file": 1}},
                "Example package B": {"CONTAINS": {"Example file": 1}},
            }
        },
        "Package without connection to document": {},
    }
    document = _create_minimal_document()
    document.packages += [
        Package(
            spdx_id="SPDXRef-Package-C",
            name="Package without connection to document",
            download_location="https://download.location.com",
        )
    ]
    opossum_information = _get_opossum_information_from_document(document)

    file_tree = opossum_information.resources.to_dict()
    assert file_tree == expected_file_tree
    TestCase().assertCountEqual(
        opossum_information.attributionBreakpoints,
        [
            "/SPDX Lite Document/DESCRIBES/",
            "/SPDX Lite Document/DESCRIBES/Example package A/CONTAINS/",
            "/SPDX Lite Document/DESCRIBES/Example package B/CONTAINS/",
        ],
    )

    assert opossum_information.resourcesToAttributions == {
        "/SPDX Lite Document/": ["SPDXRef-DOCUMENT"],
        "/SPDX Lite Document/DESCRIBES/Example package A/": ["SPDXRef-Package-A"],
        "/SPDX Lite Document/DESCRIBES/Example package A/CONTAINS/Example file": [
            "SPDXRef-File"
        ],
        "/SPDX Lite Document/DESCRIBES/Example package B/": ["SPDXRef-Package-B"],
        "/SPDX Lite Document/DESCRIBES/Example package B/CONTAINS/Example file": [
            "SPDXRef-File"
        ],
        "/Package without connection to document": ["SPDXRef-Package-C"],
    }

    TestCase().assertCountEqual(
        opossum_information.externalAttributions.keys(),
        [
            "SPDXRef-DOCUMENT",
            "SPDXRef-Package-A",
            "SPDXRef-File",
            "SPDXRef-Package-B",
            "SPDXRef-Package-C",
        ],
    )


def test_different_roots_graph() -> None:
    """Creating a tree from a connected graph where some edges are not reachable
    from the SPDX Lite Document node. This means that the connected graph has multiple
    sources and thus the result should be disconnected."""
    expected_file_tree = {
        "File-B": {"DESCRIBES": {"Package-B": {}}},
        "Document": {
            "DESCRIBES": {"Package-A": {"CONTAINS": {"File-A": 1}}, "Package-B": {}}
        },
    }
    document = _generate_document_with_from_root_node_unreachable_file()
    opossum_information = _get_opossum_information_from_document(document)

    file_tree = opossum_information.resources.to_dict()
    assert file_tree == expected_file_tree
    TestCase().assertCountEqual(
        opossum_information.attributionBreakpoints,
        [
            "/Document/DESCRIBES/",
            "/Document/DESCRIBES/Package-A/CONTAINS/",
            "/File-B/DESCRIBES/",
        ],
    )

    assert opossum_information.resourcesToAttributions == {
        "/File-B/": ["SPDXRef-File-B"],
        "/File-B/DESCRIBES/Package-B": ["SPDXRef-Package-B"],
        "/Document/": ["SPDXRef-DOCUMENT"],
        "/Document/DESCRIBES/Package-A/": ["SPDXRef-Package-A"],
        "/Document/DESCRIBES/Package-A/CONTAINS/File-A": ["SPDXRef-File-A"],
        "/Document/DESCRIBES/Package-B": ["SPDXRef-Package-B"],
    }

    TestCase().assertCountEqual(
        opossum_information.externalAttributions.keys(),
        [
            "SPDXRef-DOCUMENT",
            "SPDXRef-Package-A",
            "SPDXRef-File-A",
            "SPDXRef-File-B",
            "SPDXRef-Package-B",
        ],
    )


def test_tree_generation_for_bigger_examples_json() -> None:
    opossum_information = _get_opossum_information_from_file(
        "SPDXJSONExample-v2.3.spdx.json"
    )
    file_tree = opossum_information.resources.to_dict()

    expected_breakpoints = [
        "/SPDX-Tools-v2.0/CONTAINS/glibc/CONTAINS/"
        "lib-source/commons-lang3-3.1-sources.jar/GENERATED_FROM/",
        "/SPDX-Tools-v2.0/CONTAINS/glibc/DYNAMIC_LINK/",
    ]

    assert isinstance(file_tree, dict)
    assert len(file_tree.keys()) == 3

    for attribution_breakpoint in expected_breakpoints:
        assert attribution_breakpoint in opossum_information.attributionBreakpoints
    assert (
        file_tree["SPDX-Tools-v2.0"]["COPY_OF"][
            "DocumentRef-spdx-tool-1.2:SPDXRef-ToolsElement"
        ]
        == 1
    )

    assert (
        file_tree["SPDX-Tools-v2.0"]["CONTAINS"]["glibc"]["DYNAMIC_LINK"]["Saxon"] == {}
    )


def test_tree_generation_for_bigger_examples_spdx() -> None:
    opossum_information = _get_opossum_information_from_file("SPDX.spdx")
    file_tree = opossum_information.resources.to_dict()
    expected_breakpoints = [
        "/SPDX Lite Document/DESCRIBES/Package A/CONTAINS/",
        "/SPDX Lite Document/DESCRIBES/Package A/COPY_OF/" "Package C/CONTAINS/",
    ]

    assert isinstance(file_tree, dict)
    assert len(file_tree.keys()) == 2

    for attribution_breakpoint in expected_breakpoints:
        assert attribution_breakpoint in opossum_information.attributionBreakpoints

    assert file_tree["SPDX Lite Document"]["DESCRIBES"]["Package B"] == {}

    assert (
        file_tree["SPDX Lite Document"]["DESCRIBES"]["Package A"]["CONTAINS"]["File-C"]
        == 1
    )


def _get_opossum_information_from_file(file_name: str) -> OpossumInformation:
    document = parse_file(
        str(Path(__file__).resolve().parent.parent / "data" / file_name)
    )
    return _get_opossum_information_from_document(document)


def _get_opossum_information_from_document(document: Document) -> OpossumInformation:
    graph = generate_graph_from_spdx(document)
    tree = generate_tree_from_graph(graph)
    opossum_information = convert_tree_to_opossum_information(tree)
    return opossum_information
