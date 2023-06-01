# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Dict, List
from unittest import mock

import pytest

from opossum_lib.merger import (
    _merge_dicts_without_duplicates,
    _merge_resources,
    _merge_resources_to_attributions,
    expand_opossum_package_identifier,
    merge_opossum_information,
)
from opossum_lib.opossum_file import (
    Metadata,
    OpossumInformation,
    OpossumPackage,
    OpossumPackageIdentifier,
    Resource,
    ResourcePath,
    SourceInfo,
)


@mock.patch("opossum_lib.opossum_file.OpossumPackage", autospec=True)
def test_merge_opossum_information(opossum_package: OpossumPackage) -> None:
    opossum_information = OpossumInformation(
        Metadata("project-id", "30-05-2023", "test data"),
        Resource({"A": Resource({"B": Resource({})})}),
        {"SPDXRef-Package": opossum_package},
        {"/A/B/": ["SPDXRef-Package"]},
    )

    opossum_information_2 = OpossumInformation(
        Metadata("test-data-id", "29-05-2023", "second test data"),
        Resource({"A": Resource({"D": Resource({"C": Resource({})})})}),
        {"SPDXRef-File": opossum_package},
        {"/A/D/C": ["SPDXRef-File"]},
    )

    merged_information = merge_opossum_information(
        [opossum_information, opossum_information_2]
    )

    assert merged_information.metadata == opossum_information.metadata
    assert merged_information.resources == Resource(
        {"A": Resource({"B": Resource({}), "D": Resource({"C": Resource({})})})}
    )
    assert merged_information.externalAttributions == {
        "project-id-SPDXRef-Package": opossum_package,
        "test-data-id-SPDXRef-File": opossum_package,
    }
    assert merged_information.resourcesToAttributions == {
        "/A/B/": ["project-id-SPDXRef-Package"],
        "/A/D/C": ["test-data-id-SPDXRef-File"],
    }


def test_merge_resources() -> None:
    list_of_paths = [["A"], ["A", "B", "C"], ["A", "B"], ["A", "D"]]
    resource = Resource()

    for path in list_of_paths:
        resource.add_path(path)
    list_of_paths = [["C", "D", "E"], ["A", "B", "C"], ["A", "B"], ["A", "D"]]
    resource2 = Resource()

    for path in list_of_paths:
        resource2.add_path(path)
    resources = [resource, resource2]
    merged_resource = _merge_resources(resources)

    assert merged_resource == Resource(
        {
            "A": Resource({"B": Resource({"C": Resource({})}), "D": Resource({})}),
            "C": Resource({"D": Resource({"E": Resource({})})}),
        }
    )


@pytest.mark.parametrize(
    "resources_to_attributions, expected_resources_to_attributions",
    [
        (
            [
                {"resources/Path": ["identifier-A", "identifier-B"]},
                {"resources/Path": ["identifier-C"]},
                {"resources/Path/different": ["identifier-A"]},
            ],
            {
                "resources/Path": ["identifier-A", "identifier-B", "identifier-C"],
                "resources/Path/different": ["identifier-A"],
            },
        ),
        (
            [{"resources/Path": ["uuid_1"]}, {"resources/Path": ["uuid_1", "uuid_2"]}],
            {
                "resources/Path": ["uuid_1", "uuid_2"],
            },
        ),
    ],
)
def test_merge_resources_to_attributions(
    resources_to_attributions: List[Dict[ResourcePath, List[OpossumPackageIdentifier]]],
    expected_resources_to_attributions: Dict[
        ResourcePath, List[OpossumPackageIdentifier]
    ],
) -> None:
    merged_resources_to_attributions = _merge_resources_to_attributions(
        resources_to_attributions
    )
    assert merged_resources_to_attributions == expected_resources_to_attributions


@mock.patch("opossum_lib.opossum_file.OpossumPackage", autospec=True)
def test_merge_dicts_without_duplicates(opossum_package: OpossumPackage) -> None:
    dicts = [{"A": opossum_package}, {"B": opossum_package}]
    merged_dict = _merge_dicts_without_duplicates(dicts)

    assert merged_dict == {"A": opossum_package, "B": opossum_package}


@mock.patch("opossum_lib.opossum_file.SourceInfo", autospec=True)
def test_merge_dicts_without_duplicates_type_error(
    source_info: SourceInfo,
) -> None:
    dicts = [
        {"A": OpossumPackage(source_info, comment="test package 1")},
        {"A": OpossumPackage(source_info, comment="test package 2")},
    ]
    with pytest.raises(TypeError):
        _merge_dicts_without_duplicates(dicts)


@mock.patch("opossum_lib.opossum_file.Resource")
@mock.patch("opossum_lib.opossum_file.OpossumPackage")
def test_expand_opossum_package_identifier(
    opossum_package: OpossumPackage, resource: Resource
) -> None:
    opossum_information_expanded = expand_opossum_package_identifier(
        OpossumInformation(
            Metadata("project-id", "2022-03-02", "project title"),
            resources=resource,
            externalAttributions={"SPDXRef-Package": opossum_package},
            resourcesToAttributions={"/path/to/resource": ["SPDXRef-Package"]},
            attributionBreakpoints=[],
            externalAttributionSources={},
        )
    )

    assert opossum_information_expanded.resourcesToAttributions == {
        "/path/to/resource": ["project-id-SPDXRef-Package"]
    }
    assert opossum_information_expanded.externalAttributions == {
        "project-id-SPDXRef-Package": opossum_package
    }
