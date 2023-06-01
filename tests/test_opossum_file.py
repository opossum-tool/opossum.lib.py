# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from opossum_lib.opossum_file import Resource


def test_resource_to_dict() -> None:
    list_of_paths = [["A"], ["A", "B", "C"], ["A", "B"], ["A", "D"]]
    resource = Resource()

    for path in list_of_paths:
        resource.add_path(path)

    assert resource.to_dict() == {"A": {"B": {"C": 1}, "D": 1}}


def test_resource_get_path() -> None:
    list_of_paths = [["A", "B", "C"], ["A", "D"], ["D", "E", "F"]]
    resource = Resource()

    for path in list_of_paths:
        resource.add_path(path)

    assert resource.get_paths() == ["/A/B/C/", "/A/D/", "/D/E/F/"]
