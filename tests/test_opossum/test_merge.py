# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from unittest import mock

import pytest

from opossum_lib.opossum.merger import (
    _merge_dicts_without_duplicates,
    _merge_resources,
    _merge_resources_to_attributions,
    expand_opossum_package_identifier,
    merge_opossum_information,
)
from opossum_lib.opossum.opossum_file import (
    Metadata,
    OpossumInformation,
    OpossumPackage,
    OpossumPackageIdentifier,
    Resource,
    ResourcePath,
    ResourceType,
    SourceInfo,
)


def test_merge_opossum_information() -> None:
    opossum_package = OpossumPackage(source=SourceInfo(name="source"))
    opossum_information = OpossumInformation(
        Metadata(
            projectId="project-id",
            fileCreationDate="30-05-2023",
            projectTitle="test data",
        ),
        {"A": {"B": {}}},
        {"SPDXRef-Package": opossum_package},
        {"/A/B/": ["SPDXRef-Package"]},
    )

    opossum_information_2 = OpossumInformation(
        Metadata(
            projectId="test-data-id",
            fileCreationDate="29-05-2023",
            projectTitle="second test data",
        ),
        {"A": {"D": {"C": 1}}},
        {"SPDXRef-File": opossum_package},
        {"/A/D/C": ["SPDXRef-File"]},
    )

    merged_information = merge_opossum_information(
        [opossum_information, opossum_information_2]
    )

    assert merged_information.metadata == opossum_information.metadata
    assert merged_information.resources == {
        "A": {
            "B": {},
            "D": {"C": 1},
        }
    }
    assert merged_information.externalAttributions == {
        "project-id-SPDXRef-Package": opossum_package,
        "test-data-id-SPDXRef-File": opossum_package,
    }
    assert merged_information.resourcesToAttributions == {
        "/A/B/": ["project-id-SPDXRef-Package"],
        "/A/D/C": ["test-data-id-SPDXRef-File"],
    }


def test_merge_resources() -> None:
    list_of_paths_with_resource_types = [
        [("A", ResourceType.FOLDER)],
        [
            ("A", ResourceType.FOLDER),
            ("B", ResourceType.FOLDER),
            ("C", ResourceType.FILE),
        ],
        [("A", ResourceType.FOLDER), ("D", ResourceType.FILE)],
    ]

    resource = Resource(ResourceType.TOP_LEVEL)
    for path in list_of_paths_with_resource_types:
        resource = resource.add_path(path)

    list_of_paths_with_resource_type = [
        [("A", ResourceType.FOLDER)],
        [
            ("A", ResourceType.FOLDER),
            ("B", ResourceType.FOLDER),
            ("C", ResourceType.FILE),
        ],
        [("A", ResourceType.FOLDER), ("D", ResourceType.FILE)],
        [
            ("C", ResourceType.FOLDER),
            ("D", ResourceType.FOLDER),
            ("E", ResourceType.FOLDER),
        ],
    ]
    resource2 = Resource(ResourceType.TOP_LEVEL)
    for path in list_of_paths_with_resource_type:
        resource2 = resource2.add_path(path)

    resources = [resource, resource2]
    merged_resource = _merge_resources(resources)

    assert merged_resource == Resource(
        ResourceType.TOP_LEVEL,
        {
            "A": Resource(
                ResourceType.FOLDER,
                {
                    "B": Resource(
                        ResourceType.FOLDER, {"C": Resource(ResourceType.FILE, {})}
                    ),
                    "D": Resource(ResourceType.FILE, {}),
                },
            ),
            "C": Resource(
                ResourceType.FOLDER,
                {
                    "D": Resource(
                        ResourceType.FOLDER, {"E": Resource(ResourceType.FOLDER, {})}
                    )
                },
            ),
        },
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
    resources_to_attributions: list[dict[ResourcePath, list[OpossumPackageIdentifier]]],
    expected_resources_to_attributions: dict[
        ResourcePath, list[OpossumPackageIdentifier]
    ],
) -> None:
    merged_resources_to_attributions = _merge_resources_to_attributions(
        resources_to_attributions
    )
    assert merged_resources_to_attributions == expected_resources_to_attributions


@mock.patch("opossum_lib.opossum.opossum_file.OpossumPackage", autospec=True)
def test_merge_dicts_without_duplicates(opossum_package: OpossumPackage) -> None:
    dicts = [{"A": opossum_package}, {"B": opossum_package}]
    merged_dict = _merge_dicts_without_duplicates(dicts)

    assert merged_dict == {"A": opossum_package, "B": opossum_package}


@mock.patch("opossum_lib.opossum.opossum_file.SourceInfo", autospec=True)
def test_merge_dicts_without_duplicates_type_error(
    source_info: SourceInfo,
) -> None:
    dicts = [
        {"A": OpossumPackage(source_info, comment="test package 1")},
        {"A": OpossumPackage(source_info, comment="test package 2")},
    ]
    with pytest.raises(TypeError):
        _merge_dicts_without_duplicates(dicts)


def test_expand_opossum_package_identifier() -> None:
    opossum_package = OpossumPackage(SourceInfo(name="source-info"))
    opossum_information_expanded = expand_opossum_package_identifier(
        OpossumInformation(
            Metadata(
                projectId="project-id",
                fileCreationDate="2022-03-02",
                projectTitle="project title",
            ),
            resources={},
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
