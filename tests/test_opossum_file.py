# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
import pytest

from opossum_lib.opossum.opossum_file import Resource, ResourceType


def test_resource_to_dict_with_file_as_leaf() -> None:
    list_of_paths = [
        [("A", ResourceType.FOLDER)],
        [
            ("A", ResourceType.FOLDER),
            ("B", ResourceType.FILE),
            ("C", ResourceType.FILE),
        ],
        [("A", ResourceType.FOLDER), ("B", ResourceType.FILE)],
        [("A", ResourceType.FOLDER), ("D", ResourceType.FILE)],
    ]
    resource = Resource(ResourceType.TOP_LEVEL)

    for path in list_of_paths:
        resource = resource.add_path(path)

    assert resource.to_dict() == {"A": {"B": {"C": 1}, "D": 1}}


def test_resource_to_dict_with_package_as_leaf() -> None:
    list_of_paths = [
        [("A", ResourceType.FOLDER)],
        [
            ("A", ResourceType.FOLDER),
            ("B", ResourceType.FILE),
            ("C", ResourceType.FOLDER),
        ],
        [("A", ResourceType.FOLDER), ("B", ResourceType.FILE)],
        [("A", ResourceType.FOLDER), ("D", ResourceType.FOLDER)],
    ]
    resource = Resource(ResourceType.TOP_LEVEL)

    for path in list_of_paths:
        resource = resource.add_path(path)

    assert resource.to_dict() == {"A": {"B": {"C": {}}, "D": {}}}


def test_resource_get_path() -> None:
    list_of_paths = [
        [
            ("A", ResourceType.FOLDER),
            ("B", ResourceType.FILE),
            ("C", ResourceType.FOLDER),
        ],
        [
            ("A", ResourceType.FOLDER),
            ("D", ResourceType.FILE),
        ],
        [
            ("D", ResourceType.FOLDER),
            ("E", ResourceType.FILE),
            ("F", ResourceType.OTHER),
        ],
    ]
    resource = Resource(ResourceType.TOP_LEVEL)

    for path in list_of_paths:
        resource = resource.add_path(path)

    assert resource.get_paths_of_all_leaf_nodes_with_types() == [
        [
            ("A", ResourceType.FOLDER),
            ("B", ResourceType.FILE),
            ("C", ResourceType.FOLDER),
        ],
        [
            ("A", ResourceType.FOLDER),
            ("D", ResourceType.FILE),
        ],
        [
            ("D", ResourceType.FOLDER),
            ("E", ResourceType.FILE),
            ("F", ResourceType.OTHER),
        ],
    ]


def test_resource_add_path_throws_err_if_leaf_element_exists_with_different_type() -> (
    None
):
    resource = Resource(ResourceType.TOP_LEVEL)
    resource = resource.add_path(
        [
            ("A", ResourceType.FOLDER),
            ("B", ResourceType.FILE),
            ("C", ResourceType.FOLDER),
        ]
    )

    with pytest.raises(TypeError):
        resource.add_path(
            [
                ("A", ResourceType.FOLDER),
                ("B", ResourceType.FILE),
                ("C", ResourceType.FILE),
            ]
        )


def test_resource_add_path_throws_err_if_element_exists_with_different_type() -> None:
    resource = Resource(ResourceType.TOP_LEVEL)
    resource = resource.add_path(
        [
            ("A", ResourceType.FOLDER),
            ("B", ResourceType.FILE),
            ("C", ResourceType.FOLDER),
            ("D", ResourceType.FILE),
        ]
    )

    with pytest.raises(TypeError):
        resource.add_path(
            [
                ("A", ResourceType.FOLDER),
                ("B", ResourceType.FILE),
                ("C", ResourceType.FILE),
            ]
        )


def test_resource_drop_element_error() -> None:
    resource = Resource(ResourceType.TOP_LEVEL)
    resource = resource.add_path(
        [
            ("A", ResourceType.FOLDER),
            ("B", ResourceType.FILE),
            ("E", ResourceType.FOLDER),
            ("D", ResourceType.FILE),
        ]
    )

    with pytest.raises(ValueError):
        resource.drop_element(
            [
                ("A", ResourceType.FOLDER),
                ("B", ResourceType.FILE),
                ("C", ResourceType.FILE),
            ]
        )


def test_resource_drop_element_error_not_leaf() -> None:
    resource = Resource(ResourceType.TOP_LEVEL)
    resource = resource.add_path(
        [
            ("A", ResourceType.FOLDER),
            ("B", ResourceType.FILE),
            ("C", ResourceType.FOLDER),
            ("D", ResourceType.FILE),
        ]
    )

    with pytest.raises(ValueError):
        resource.drop_element(
            [
                ("A", ResourceType.FOLDER),
                ("B", ResourceType.FILE),
                ("C", ResourceType.FILE),
            ]
        )


def test_resource_drop_element() -> None:
    resource = Resource(ResourceType.TOP_LEVEL)
    resource = resource.add_path(
        [
            ("A", ResourceType.FOLDER),
            ("B", ResourceType.FILE),
            ("C", ResourceType.FOLDER),
        ]
    )

    resource_without_element = resource.drop_element(
        [
            ("A", ResourceType.FOLDER),
            ("B", ResourceType.FILE),
            ("C", ResourceType.FOLDER),
        ]
    )

    assert resource_without_element.get_paths_of_all_leaf_nodes_with_types() == [
        [("A", ResourceType.FOLDER), ("B", ResourceType.FILE)]
    ]
