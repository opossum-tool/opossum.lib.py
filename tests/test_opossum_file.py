# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
import pytest

from opossum_lib.opossum_file import Resource, ResourceType


def test_resource_to_dict_with_file_as_leaf() -> None:
    list_of_paths = [["A"], ["A", "B", "C"], ["A", "B"], ["A", "D"]]
    resource = Resource(ResourceType.TOP_LEVEL)

    for path in list_of_paths:
        resource.add_path(path, ResourceType.FILE)

    assert resource.to_dict() == {"A": {"B": {"C": 1}, "D": 1}}


def test_resource_to_dict_with_package_as_leaf() -> None:
    list_of_paths = [["A"], ["A", "B", "C"], ["A", "B"], ["A", "D"]]
    resource = Resource(ResourceType.TOP_LEVEL)

    for path in list_of_paths:
        resource.add_path(path, ResourceType.FOLDER)

    assert resource.to_dict() == {"A": {"B": {"C": {}}, "D": {}}}


def test_resource_get_path() -> None:
    list_of_paths = [
        (["A", "B", "C"], ResourceType.FOLDER),
        (["A", "D"], ResourceType.FILE),
        (["D", "E", "F"], ResourceType.OTHER),
    ]
    resource = Resource(ResourceType.TOP_LEVEL)

    for path, resource_type in list_of_paths:
        resource.add_path(path, resource_type)

    assert resource.get_paths_with_resource_types() == [
        ("/A/B/C/", ResourceType.FOLDER),
        ("/A/D", ResourceType.FILE),
        ("/D/E/F", ResourceType.OTHER),
    ]


def test_resource_add_path_type_error() -> None:
    resource = Resource(ResourceType.TOP_LEVEL)
    resource.add_path(["A", "B", "C"], ResourceType.FOLDER)

    with pytest.raises(TypeError):
        resource.add_path(["A", "B", "C"], ResourceType.FILE)
