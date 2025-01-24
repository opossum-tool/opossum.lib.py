# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0


from opossum_lib.opossum_model import OpossumPackage, SourceInfo
from opossum_lib.scancode.constants import SCANCODE_SOURCE_NAME
from opossum_lib.scancode.convert_scancode_to_opossum import get_attribution_info
from tests.test_setup.scancode_faker_setup import ScanCodeFaker


def test_get_attribution_info_directory(scancode_faker: ScanCodeFaker) -> None:
    folder = scancode_faker.single_folder(path="some/single/folder")
    assert get_attribution_info(folder) == []


def test_get_attribution_info_from_file_without_detections(
    scancode_faker: ScanCodeFaker,
) -> None:
    file = scancode_faker.single_file(path="some/single/file", license_detections=[])
    assert get_attribution_info(file) == []


def test_get_attribution_info_file_multiple(scancode_faker: ScanCodeFaker) -> None:
    match1 = scancode_faker.match(
        license_expression_spdx="Apache-2.0",
        from_file="A",
        score=75,
        rule_relevance=50,
    )
    match2 = scancode_faker.match(
        license_expression_spdx="Apache-2.0",
        from_file="A",
        score=95,
        rule_relevance=50,
    )
    match3 = scancode_faker.match(
        license_expression_spdx="MIT",
        from_file="A",
        score=50,
        rule_relevance=50,
    )
    license1 = scancode_faker.license_detection(
        license_expression_spdx="Apache-2.0",
        matches=[match1, match2],
    )
    license2 = scancode_faker.license_detection(
        license_expression_spdx="MIT",
        matches=[match3],
    )
    copyright1 = scancode_faker.copyright(copyright="Me")
    copyright2 = scancode_faker.copyright(copyright="Myself")
    copyright3 = scancode_faker.copyright(copyright="I")
    file = scancode_faker.single_file(
        path="A",
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
