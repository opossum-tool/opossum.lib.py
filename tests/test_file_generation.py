# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
from typing import List, Tuple
from unittest import TestCase

import pytest
from spdx_tools.spdx.model.package import Package
from spdx_tools.spdx.parser.parse_anything import parse_file

from opossum_lib.file_generation import generate_json_file_from_tree
from opossum_lib.graph_generation import generate_graph_from_spdx
from opossum_lib.tree_generation import generate_tree_from_graph
from tests.helper_methods import (
    _create_minimal_document,
    _generate_document_with_from_root_node_unreachable_file,
)


def test_different_paths_graph() -> None:
    """Creating a tree from a directed graph with a cycle."""
    expected_file_tree = {
        "SPDXRef-DOCUMENT": {
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
            "/SPDXRef-DOCUMENT/DESCRIBES/",
            "/SPDXRef-DOCUMENT/DESCRIBES/Example package A/CONTAINS/",
            "/SPDXRef-DOCUMENT/DESCRIBES/Example package B/CONTAINS/",
        ],
    )
    assert opossum_information.resourcesToAttributions == {
        "/SPDXRef-DOCUMENT/": ["SPDXRef-DOCUMENT"],
        "/SPDXRef-DOCUMENT/DESCRIBES/Example package A/": [
            "SPDXRef-Package-A",
            "package-identifier",
        ],
        "/SPDXRef-DOCUMENT/DESCRIBES/Example package A/CONTAINS/Example file": [
            "SPDXRef-File",
            "file-identifier",
        ],
        "/SPDXRef-DOCUMENT/DESCRIBES/Example package B/": [
            "SPDXRef-Package-B",
            "package-identifier",
        ],
        "/SPDXRef-DOCUMENT/DESCRIBES/Example package B/CONTAINS/Example file": [
            "SPDXRef-File",
            "file-identifier",
        ],
    }

    TestCase().assertCountEqual(
        opossum_information.externalAttributions.keys(),
        [
            "SPDXRef-DOCUMENT",
            "SPDXRef-Package-A",
            "package-identifier",
            "SPDXRef-File",
            "file-identifier",
            "SPDXRef-Package-B",
            "snippet-identifier",
        ],
    )


def test_unconnected_paths_graph() -> None:
    """Creating a tree from a directed graph with a cycle."""
    expected_file_tree = {
        "SPDXRef-DOCUMENT": {
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
            "/SPDXRef-DOCUMENT/DESCRIBES/",
            "/SPDXRef-DOCUMENT/DESCRIBES/Example package A/CONTAINS/",
            "/SPDXRef-DOCUMENT/DESCRIBES/Example package B/CONTAINS/",
        ],
    )

    assert opossum_information.resourcesToAttributions == {
        "/SPDXRef-DOCUMENT/": ["SPDXRef-DOCUMENT"],
        "/SPDXRef-DOCUMENT/DESCRIBES/Example package A/": [
            "SPDXRef-Package-A",
            "package-identifier",
        ],
        "/SPDXRef-DOCUMENT/DESCRIBES/Example package A/CONTAINS/Example file": [
            "SPDXRef-File",
            "file-identifier",
        ],
        "/SPDXRef-DOCUMENT/DESCRIBES/Example package B/": [
            "SPDXRef-Package-B",
            "package-identifier",
        ],
        "/SPDXRef-DOCUMENT/DESCRIBES/Example package B/CONTAINS/Example file": [
            "SPDXRef-File",
            "file-identifier",
        ],
        "/Package without connection to document": [
            "SPDXRef-Package-C",
            "package-identifier",
        ],
    }

    TestCase().assertCountEqual(
        opossum_information.externalAttributions.keys(),
        [
            "SPDXRef-DOCUMENT",
            "SPDXRef-Package-A",
            "package-identifier",
            "SPDXRef-File",
            "file-identifier",
            "SPDXRef-Package-B",
            "snippet-identifier",
            "SPDXRef-Package-C",
        ],
    )


def test_different_roots_graph() -> None:
    """Creating a tree from a connected graph where some edges are not reachable
    from the SPDXRef-DOCUMENT node. This means that the connected graph has multiple
    sources and thus the result should be disconnected."""
    expected_file_tree = {
        "File-B": {"DESCRIBES": {"Package-B": 1}},
        "SPDXRef-DOCUMENT": {
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
            "/SPDXRef-DOCUMENT/DESCRIBES/",
            "/SPDXRef-DOCUMENT/DESCRIBES/Package-A/CONTAINS/",
            "/File-B/DESCRIBES/",
        ],
    )

    assert opossum_information.resourcesToAttributions == {
        "/File-B/": ["SPDXRef-File-B", "file-identifier"],
        "/File-B/DESCRIBES/Package-B": ["SPDXRef-Package-B", "package-identifier"],
        "/SPDXRef-DOCUMENT/": ["SPDXRef-DOCUMENT"],
        "/SPDXRef-DOCUMENT/DESCRIBES/Package-A/": [
            "SPDXRef-Package-A",
            "package-identifier",
        ],
        "/SPDXRef-DOCUMENT/DESCRIBES/Package-A/CONTAINS/File-A": [
            "SPDXRef-File-A",
            "file-identifier",
        ],
        "/SPDXRef-DOCUMENT/DESCRIBES/Package-B": [
            "SPDXRef-Package-B",
            "package-identifier",
        ],
    }

    TestCase().assertCountEqual(
        opossum_information.externalAttributions.keys(),
        [
            "SPDXRef-DOCUMENT",
            "SPDXRef-Package-A",
            "package-identifier",
            "SPDXRef-File-A",
            "SPDXRef-File-B",
            "file-identifier",
            "SPDXRef-Package-B",
            "snippet-identifier",
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
                "SPDXRef-DOCUMENT",
                "COPY_OF",
                "DocumentRef-spdx-tool-1.2:SPDXRef-ToolsElement",
            ),
            (
                "SPDXRef-DOCUMENT",
                "CONTAINS",
                "glibc",
                "DYNAMIC_LINK",
                "Saxon",
            ),
            [
                "/SPDXRef-DOCUMENT/CONTAINS/glibc/CONTAINS/"
                "lib-source/commons-lang3-3.1-sources.jar/GENERATED_FROM/",
                "/SPDXRef-DOCUMENT/CONTAINS/glibc/DYNAMIC_LINK/",
            ],
        ),
        (
            "SPDX.spdx",
            2,
            ("SPDXRef-DOCUMENT", "DESCRIBES", "Package B"),
            (
                "SPDXRef-DOCUMENT",
                "DESCRIBES",
                "Package A",
                "CONTAINS",
                "File-C",
            ),
            [
                "/SPDXRef-DOCUMENT/DESCRIBES/Package A/CONTAINS/",
                "/SPDXRef-DOCUMENT/DESCRIBES/Package A/COPY_OF/" "Package C/CONTAINS/",
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
