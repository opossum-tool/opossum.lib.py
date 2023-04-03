# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
from unittest import TestCase

import pytest
from spdx.model.package import Package
from spdx.parser.parse_anything import parse_file

from opossum_lib.file_generation import generate_json_file_from_tree, write_dict_to_file
from opossum_lib.graph_generation import generate_graph_from_spdx
from opossum_lib.tree_generation import generate_tree_from_graph
from tests.helper_methods import (
    _create_minimal_document,
    _generate_document_with_from_root_node_unreachable_file,
)


def test_different_paths_graph() -> None:
    # generate tree from a directed graph with a cycle
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
        ["metadata", "resources", "externalAttributions", "resourcesToAttributions"],
        list(opossum_information.keys()),
    )
    file_tree = opossum_information["resources"]
    assert file_tree == expected_file_tree


def test_unconnected_paths_graph() -> None:
    # generate tree from a directed graph with a cycle
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

    write_dict_to_file(opossum_information, "example2.json")
    TestCase().assertCountEqual(
        ["metadata", "resources", "externalAttributions", "resourcesToAttributions"],
        list(opossum_information.keys()),
    )
    file_tree = opossum_information["resources"]
    assert file_tree == expected_file_tree


def test_different_roots_graph() -> None:
    # test tree generation for a connected graph where some edges are not reachable
    # from the SPDXRef-DOCUMENT node that means the connected graph has multiple sources
    # and the result should be disconnected
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
        ["metadata", "resources", "externalAttributions", "resourcesToAttributions"],
        list(opossum_information.keys()),
    )
    file_tree = opossum_information["resources"]
    assert file_tree == expected_file_tree


@pytest.mark.parametrize(
    "file_name, expected_top_level_keys",
    [("SPDXJSONExample-v2.3.spdx.json", 3), ("SPDX.spdx", 2)],
)
def test_tree_generation_for_bigger_examples(
    file_name: str, expected_top_level_keys: int
) -> None:
    document = parse_file(str(Path(__file__).resolve().parent / "data" / file_name))
    graph = generate_graph_from_spdx(document)
    tree = generate_tree_from_graph(graph)
    opossum_information = generate_json_file_from_tree(tree)

    TestCase().assertCountEqual(
        ["metadata", "resources", "externalAttributions", "resourcesToAttributions"],
        list(opossum_information.keys()),
    )
    file_tree = opossum_information["resources"]
    assert len(file_tree.keys()) == expected_top_level_keys
