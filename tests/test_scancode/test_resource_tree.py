# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

from copy import deepcopy

from opossum_lib.opossum_model import OpossumPackage, SourceInfo
from opossum_lib.scancode.constants import SCANCODE_SOURCE_NAME
from opossum_lib.scancode.model import (
    Copyright,
    FileBasedLicenseDetection,
    FileType,
    Match,
)
from opossum_lib.scancode.resource_tree import (
    get_attribution_info,
)
from tests.test_scancode.model_helpers import _create_file


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
        source=SourceInfo(name=SCANCODE_SOURCE_NAME),
        license_name="Apache-2.0",
        copyright="Me\nMyself\nI",
        attribution_confidence=95,
    )
    expected2 = OpossumPackage(
        source=SourceInfo(name=SCANCODE_SOURCE_NAME),
        license_name="MIT",
        copyright="Me\nMyself\nI",
        attribution_confidence=50,
    )
    assert set(attributions) == {expected1, expected2}
