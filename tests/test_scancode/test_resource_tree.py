# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

from copy import deepcopy
from typing import Any
from unittest import mock

import pytest
from pydantic import ValidationError

from opossum_lib.opossum.opossum_file import OpossumPackage, SourceInfo
from opossum_lib.scancode.constants import SCANCODE_SOURCE_NAME
from opossum_lib.scancode.model import (
    Copyright,
    File,
    FileBasedLicenseDetection,
    FileType,
    Match,
    ScanCodeData,
)
from opossum_lib.scancode.resource_tree import (
    ScanCodeFileTree,
    convert_to_opossum_resources,
    create_attribution_mapping,
    get_attribution_info,
    scancode_to_file_tree,
)
from tests.test_scancode.model_helpers import _create_file


class TestRevalidate:
    def test_successfully_revalidate_valid_file_tree(self) -> None:
        dummy_file = _create_file("A", FileType.FILE)
        valid_structure = ScanCodeFileTree(
            file=dummy_file,
            children={
                "A": ScanCodeFileTree(file=dummy_file),
                "B": ScanCodeFileTree(
                    file=dummy_file, children={"C": ScanCodeFileTree(file=dummy_file)}
                ),
            },
        )
        valid_structure.revalidate()

    def test_fail_to_revalidate_file_tree_invalid_at_toplevel(self) -> None:
        dummy_file = _create_file("A", FileType.FILE)
        invalid_structure = ScanCodeFileTree.model_construct(
            children={
                "A": ScanCodeFileTree(file=dummy_file),
                "B": ScanCodeFileTree(
                    file=dummy_file, children={"C": ScanCodeFileTree(file=dummy_file)}
                ),
            },
            file=None,  # type: ignore
        )
        with pytest.raises(ValidationError):
            invalid_structure.revalidate()

    def test_fail_to_revalidate_file_tree_invalid_only_at_lower_level(self) -> None:
        dummy_file = _create_file("A", FileType.FILE)
        invalid_structure = ScanCodeFileTree(
            file=dummy_file,
            children={
                "A": ScanCodeFileTree(file=dummy_file),
                "B": ScanCodeFileTree(
                    file=dummy_file,
                    children={"C": ScanCodeFileTree.model_construct(None)},  # type: ignore
                ),
            },
        )
        with pytest.raises(ValidationError):
            invalid_structure.revalidate()


def test_scancode_to_resource_tree_produces_expected_result() -> None:
    files = _create_reference_scancode_files()
    scancode_data = ScanCodeData(
        headers=[], packages=[], dependencies=[], license_detections=[], files=files
    )

    tree = scancode_to_file_tree(scancode_data)
    reference = _create_reference_node_structure()

    assert tree == reference


def test_convert_to_opossum_resources_produces_expected_result() -> None:
    scancode_data = ScanCodeData(
        headers=[],
        packages=[],
        dependencies=[],
        license_detections=[],
        files=_create_reference_scancode_files(),
    )

    tree = scancode_to_file_tree(scancode_data)
    resources = convert_to_opossum_resources(tree)
    reference = {"A": {"B": {"file3": 1}, "file1": 1, "file2.txt": 1}}
    assert resources == reference


@mock.patch(
    "opossum_lib.scancode.resource_tree.get_attribution_info",
    autospec=True,
    return_value=[OpossumPackage(source=SourceInfo(name="mocked"))],
)
def test_create_attribution_mapping_paths_have_root_prefix(_: Any) -> None:
    rootnode = _create_reference_node_structure()
    _, resources_to_attributions = create_attribution_mapping(rootnode)
    # OpossumUI automatically prepends every path with a "/"
    # So our resourcesToAttributions needs to start every path with "/"
    # even though ScanCode paths don't start with "/".
    assert "/A/file1" in resources_to_attributions
    assert "/A/file2.txt" in resources_to_attributions
    assert "/A/B/file3" in resources_to_attributions


def test_create_attribution_mapping() -> None:
    _, _, file1, file2, file3 = _create_reference_scancode_files()
    pkg1 = OpossumPackage(source=SourceInfo(name="S1"))
    pkg2 = OpossumPackage(source=SourceInfo(name="S2"))
    pkg3 = OpossumPackage(source=SourceInfo(name="S3"))

    def get_attribution_info_mock(file: File) -> list[OpossumPackage]:
        if file == file1:
            return [deepcopy(pkg1), deepcopy(pkg2)]
        elif file == file2:
            return [deepcopy(pkg1), deepcopy(pkg2), deepcopy(pkg3)]
        elif file == file3:
            return []
        else:
            return []

    root_node = _create_reference_node_structure()

    with mock.patch(
        "opossum_lib.scancode.resource_tree.get_attribution_info",
        new=get_attribution_info_mock,
    ):
        external_attributions, resources_to_attributions = create_attribution_mapping(
            root_node
        )
    assert len(external_attributions) == 3  # deduplication worked

    reverse_mapping = {v: k for (k, v) in external_attributions.items()}
    id1, id2, id3 = reverse_mapping[pkg1], reverse_mapping[pkg2], reverse_mapping[pkg3]
    assert len(resources_to_attributions) == 2  # only files with attributions
    assert set(resources_to_attributions["/" + file1.path]) == {id1, id2}
    assert set(resources_to_attributions["/" + file2.path]) == {id1, id2, id3}


def test_get_attribution_info_directory() -> None:
    folder = _create_file("A", FileType.DIRECTORY)
    assert get_attribution_info(folder) == []


def test_get_attribution_info_file_missing() -> None:
    file = _create_file("A", FileType.FILE)
    assert get_attribution_info(file) == []


def test_get_attribution_info_file_multiple() -> None:
    match1 = Match(
        license_expression="apache-2.0",
        license_expression_spdx="Apache-2.0",
        from_file="A",
        start_line=1,
        end_line=2,
        matcher="matcher",
        score=75,
        matched_length=1,
        match_coverage=0.5,
        rule_relevance=50,
        rule_identifier="myrule",
        rule_url="",
    )
    match2 = Match(
        license_expression="apache-2.0",
        license_expression_spdx="Apache-2.0",
        from_file="A",
        start_line=2,
        end_line=3,
        matcher="matcher",
        score=95,
        matched_length=1,
        match_coverage=0.5,
        rule_relevance=50,
        rule_identifier="hyrule",
        rule_url="",
    )
    match3 = deepcopy(match1)
    match3.score = 50
    match3.license_expression = "mit"
    match3.license_expression_spdx = "MIT"
    license1 = FileBasedLicenseDetection(
        license_expression="apache-2.0",
        license_expression_spdx="Apache-2.0",
        identifier="identifier1",
        matches=[match1, match2],
    )
    license2 = FileBasedLicenseDetection(
        license_expression="mit",
        license_expression_spdx="MIT",
        identifier="identifier2",
        matches=[match3],
    )
    copyright1 = Copyright(copyright="Me", start_line=1, end_line=2)
    copyright2 = Copyright(copyright="Myself", start_line=1, end_line=2)
    copyright3 = Copyright(copyright="I", start_line=1, end_line=2)
    file = _create_file(
        "A",
        FileType.FILE,
        license_detections=[license1, license2],
        copyrights=[copyright1, copyright2, copyright3],
    )
    attributions = get_attribution_info(file)
    expected1 = OpossumPackage(
        source=SourceInfo(SCANCODE_SOURCE_NAME),
        licenseName="Apache-2.0",
        copyright="Me\nMyself\nI",
        attributionConfidence=95,
    )
    expected2 = OpossumPackage(
        source=SourceInfo(SCANCODE_SOURCE_NAME),
        licenseName="MIT",
        copyright="Me\nMyself\nI",
        attributionConfidence=50,
    )
    assert set(attributions) == {expected1, expected2}


def _create_reference_scancode_files() -> list[File]:
    return [
        _create_file("A", FileType.DIRECTORY),
        _create_file("A/B", FileType.DIRECTORY),
        _create_file("A/file1", FileType.FILE),
        _create_file("A/file2.txt", FileType.FILE),
        _create_file("A/B/file3", FileType.FILE),
    ]


def _create_reference_node_structure() -> ScanCodeFileTree:
    folder, subfolder, file1, file2, file3 = _create_reference_scancode_files()
    inner = ScanCodeFileTree(
        file=subfolder, children={"file3": ScanCodeFileTree(file=file3)}
    )
    reference = ScanCodeFileTree(
        file=folder,
        children={
            "B": inner,
            "file1": ScanCodeFileTree(file=file1),
            "file2.txt": ScanCodeFileTree(file=file2),
        },
    )
    return reference
