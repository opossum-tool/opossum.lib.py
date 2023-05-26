# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
from typing import List, Tuple
from unittest import TestCase

import pytest
from spdx_tools.spdx.model.package import Package
from spdx_tools.spdx.parser.parse_anything import parse_file

from opossum_lib.constants import (
    SPDX_FILE_IDENTIFIER,
    SPDX_PACKAGE_IDENTIFIER,
    SPDX_SNIPPET_IDENTIFIER,
)
from opossum_lib.file_generation import generate_json_file_from_tree
from opossum_lib.graph_generation import generate_graph_from_spdx
from opossum_lib.opossum_file import ExternalAttributionSource
from opossum_lib.tree_generation import generate_tree_from_graph
from tests.helper_methods import (
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

    graph = generate_graph_from_spdx(document)
    tree = generate_tree_from_graph(graph)

    opossum_information = generate_json_file_from_tree(tree)

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
        "Package without connection to document": 1,
    }
    document = _create_minimal_document()
    document.packages += [
        Package(
            spdx_id="SPDXRef-Package-C",
            name="Package without connection to document",
            download_location="https://download.location.com",
        )
    ]

    graph = generate_graph_from_spdx(document)
    tree = generate_tree_from_graph(graph)

    opossum_information = generate_json_file_from_tree(tree)

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
        "File-B": {"DESCRIBES": {"Package-B": 1}},
        "Document": {
            "DESCRIBES": {"Package-A": {"CONTAINS": {"File-A": 1}}, "Package-B": 1}
        },
    }
    document = _generate_document_with_from_root_node_unreachable_file()

    graph = generate_graph_from_spdx(document)
    tree = generate_tree_from_graph(graph)
    opossum_information = generate_json_file_from_tree(tree)

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


@pytest.mark.parametrize(
    "file_name, expected_top_level_keys, expected_file_path_level_1, "
    "expected_file_path_level_2, expected_breakpoints",
    [
        (
            "SPDXJSONExample-v2.3.spdx.json",
            3,
            (
                "SPDX-Tools-v2.0",
                "COPY_OF",
                "DocumentRef-spdx-tool-1.2:SPDXRef-ToolsElement",
            ),
            (
                "SPDX-Tools-v2.0",
                "CONTAINS",
                "glibc",
                "DYNAMIC_LINK",
                "Saxon",
            ),
            [
                "/SPDX-Tools-v2.0/CONTAINS/glibc/CONTAINS/"
                "lib-source/commons-lang3-3.1-sources.jar/GENERATED_FROM/",
                "/SPDX-Tools-v2.0/CONTAINS/glibc/DYNAMIC_LINK/",
            ],
        ),
        (
            "SPDX.spdx",
            2,
            ("SPDX Lite Document", "DESCRIBES", "Package B"),
            (
                "SPDX Lite Document",
                "DESCRIBES",
                "Package A",
                "CONTAINS",
                "File-C",
            ),
            [
                "/SPDX Lite Document/DESCRIBES/Package A/CONTAINS/",
                "/SPDX Lite Document/DESCRIBES/Package A/COPY_OF/"
                "Package C/CONTAINS/",
            ],
        ),
    ],
)
def test_tree_generation_for_bigger_examples(
    file_name: str,
    expected_top_level_keys: int,
    expected_file_path_level_1: Tuple[str, str, str],
    expected_file_path_level_2: Tuple[str, str, str, str, str],
    expected_breakpoints: List[str],
) -> None:
    document = parse_file(str(Path(__file__).resolve().parent / "data" / file_name))
    graph = generate_graph_from_spdx(document)
    tree = generate_tree_from_graph(graph)
    opossum_information = generate_json_file_from_tree(tree)

    file_tree = opossum_information.resources.to_dict()
    assert isinstance(file_tree, dict)
    assert len(file_tree.keys()) == expected_top_level_keys
    assert (
        file_tree[expected_file_path_level_1[0]][expected_file_path_level_1[1]][
            expected_file_path_level_1[2]
        ]
        == 1
    )
    assert (
        file_tree[expected_file_path_level_2[0]][expected_file_path_level_2[1]][
            expected_file_path_level_2[2]
        ][expected_file_path_level_2[3]][expected_file_path_level_2[4]]
        == 1
    )

    for attribution_breakpoint in expected_breakpoints:
        assert attribution_breakpoint in opossum_information.attributionBreakpoints
