# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
from typing import List, Tuple
from unittest import TestCase

import pytest
from spdx.model.package import Package
from spdx.parser.parse_anything import parse_file

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
                "SPDXRef-Package-A": {"CONTAINS": {"SPDXRef-File": 1}},
                "SPDXRef-Package-B": {"CONTAINS": {"SPDXRef-File": 1}},
            }
        }
    }
    document = _create_minimal_document()

    graph = generate_graph_from_spdx(document)
    tree = generate_tree_from_graph(graph)

    opossum_information = generate_json_file_from_tree(tree)

    TestCase().assertCountEqual(
        [
            "metadata",
            "resources",
            "externalAttributions",
            "resourcesToAttributions",
            "attributionBreakpoints",
        ],
        list(opossum_information.keys()),
    )
    file_tree = opossum_information["resources"]
    assert file_tree == expected_file_tree
    TestCase().assertCountEqual(
        opossum_information["attributionBreakpoints"],
        [
            "/SPDXRef-DOCUMENT/SPDXRef-DOCUMENT_DESCRIBES/",
            "/SPDXRef-DOCUMENT/SPDXRef-DOCUMENT_DESCRIBES/SPDXRef-Package-A/"
            "SPDXRef-Package-A_CONTAINS/",
            "/SPDXRef-DOCUMENT/SPDXRef-DOCUMENT_DESCRIBES/SPDXRef-Package-B/"
            "SPDXRef-Package-B_CONTAINS/",
        ],
    )


def test_unconnected_paths_graph() -> None:
    """Creating a tree from a directed graph with a cycle."""
    expected_file_tree = {
        "SPDXRef-DOCUMENT": {
            "DESCRIBES": {
                "SPDXRef-Package-A": {"CONTAINS": {"SPDXRef-File": 1}},
                "SPDXRef-Package-B": {"CONTAINS": {"SPDXRef-File": 1}},
            }
        },
        "SPDXRef-Package-C": 1,
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

    TestCase().assertCountEqual(
        [
            "metadata",
            "resources",
            "externalAttributions",
            "resourcesToAttributions",
            "attributionBreakpoints",
        ],
        list(opossum_information.keys()),
    )
    file_tree = opossum_information["resources"]
    assert file_tree == expected_file_tree
    TestCase().assertCountEqual(
        opossum_information["attributionBreakpoints"],
        [
            "/SPDXRef-DOCUMENT/SPDXRef-DOCUMENT_DESCRIBES/",
            "/SPDXRef-DOCUMENT/SPDXRef-DOCUMENT_DESCRIBES/SPDXRef-Package-A/"
            "SPDXRef-Package-A_CONTAINS/",
            "/SPDXRef-DOCUMENT/SPDXRef-DOCUMENT_DESCRIBES/SPDXRef-Package-B/"
            "SPDXRef-Package-B_CONTAINS/",
        ],
    )


def test_different_roots_graph() -> None:
    """Creating a tree from a connected graph where some edges are not reachable
    from the SPDXRef-DOCUMENT node. This means that the connected graph has multiple
    sources and thus the result should be disconnected."""
    expected_file_tree = {
        "SPDXRef-DOCUMENT": {
            "DESCRIBES": {
                "SPDXRef-Package-A": {"CONTAINS": {"SPDXRef-File-A": 1}},
                "SPDXRef-Package-B": 1,
            },
        },
        "SPDXRef-File-B": {"DESCRIBES": {"SPDXRef-Package-B": 1}},
    }
    document = _generate_document_with_from_root_node_unreachable_file()

    graph = generate_graph_from_spdx(document)
    tree = generate_tree_from_graph(graph)
    opossum_information = generate_json_file_from_tree(tree)

    TestCase().assertCountEqual(
        [
            "metadata",
            "resources",
            "externalAttributions",
            "resourcesToAttributions",
            "attributionBreakpoints",
        ],
        list(opossum_information.keys()),
    )
    file_tree = opossum_information["resources"]
    assert file_tree == expected_file_tree
    TestCase().assertCountEqual(
        opossum_information["attributionBreakpoints"],
        [
            "/SPDXRef-DOCUMENT/SPDXRef-DOCUMENT_DESCRIBES/",
            "/SPDXRef-DOCUMENT/SPDXRef-DOCUMENT_DESCRIBES/SPDXRef-Package-A/"
            "SPDXRef-Package-A_CONTAINS/",
            "/SPDXRef-File-B/SPDXRef-File-B_DESCRIBES/",
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
                "SPDXRef-Package",
                "DYNAMIC_LINK",
                "SPDXRef-Saxon",
            ),
            [
                "/SPDXRef-DOCUMENT/SPDXRef-DOCUMENT_CONTAINS/SPDXRef-Package/"
                "SPDXRef-Package_CONTAINS/"
                "SPDXRef-CommonsLangSrc/SPDXRef-CommonsLangSrc_GENERATED_FROM/",
                "/SPDXRef-DOCUMENT/SPDXRef-DOCUMENT_CONTAINS/SPDXRef-Package/"
                "SPDXRef-Package_DYNAMIC_LINK/",
            ],
        ),
        (
            "SPDX.spdx",
            2,
            ("SPDXRef-DOCUMENT", "DESCRIBES", "SPDXRef-Package-B"),
            (
                "SPDXRef-DOCUMENT",
                "DESCRIBES",
                "SPDXRef-Package-A",
                "CONTAINS",
                "SPDXRef-File-C",
            ),
            [
                "/SPDXRef-DOCUMENT/SPDXRef-DOCUMENT_DESCRIBES/SPDXRef-Package-A/"
                "SPDXRef-Package-A_CONTAINS/",
                "/SPDXRef-DOCUMENT/SPDXRef-DOCUMENT_DESCRIBES/SPDXRef-Package-A/"
                "SPDXRef-Package-A_COPY_OF/"
                "SPDXRef-Package-C/SPDXRef-Package-C_CONTAINS/",
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

    TestCase().assertCountEqual(
        [
            "metadata",
            "resources",
            "externalAttributions",
            "resourcesToAttributions",
            "attributionBreakpoints",
        ],
        list(opossum_information.keys()),
    )
    file_tree = opossum_information["resources"]
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
        assert attribution_breakpoint in opossum_information["attributionBreakpoints"]
