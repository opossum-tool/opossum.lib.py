# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0


import pytest
from _pytest.logging import LogCaptureFixture

from opossum_lib.opossum_model import Resource
from opossum_lib.scancode.convert_scancode_to_opossum import (
    convert_scancode_to_opossum,
)
from tests.test_setup.scancode_faker_setup import ScanCodeFaker


def test_extract_scancode_header_produces_expected_result(
    scancode_faker: ScanCodeFaker,
) -> None:
    scancode_data = scancode_faker.scancode_data()
    opossum = convert_scancode_to_opossum(
        scancode_data,
    )
    metadata = opossum.scan_results.metadata
    header = scancode_data.headers[0]
    assert metadata.file_creation_date == header.end_timestamp
    assert metadata.project_title == "ScanCode file"


def test_extract_scancode_header_errors_with_missing_header(
    caplog: LogCaptureFixture, scancode_faker: ScanCodeFaker
) -> None:
    scancode_data = scancode_faker.scancode_data(headers=[])

    with pytest.raises(SystemExit):
        convert_scancode_to_opossum(scancode_data)

    assert "header" in caplog.messages[0].lower()


def test_extract_scancode_header_error_with_multiple_headers(
    caplog: LogCaptureFixture, scancode_faker: ScanCodeFaker
) -> None:
    header1 = scancode_faker.header()
    header2 = scancode_faker.header()
    scancode_data = scancode_faker.scancode_data(headers=[header1, header2])

    with pytest.raises(SystemExit):
        convert_scancode_to_opossum(scancode_data)

    assert "header" in caplog.messages[0].lower()


def count_resources(resource: Resource) -> int:
    return 1 + sum(count_resources(child) for child in resource.children.values())


def count_attributions(resource: Resource) -> int:
    return len(resource.attributions) + sum(
        count_attributions(child) for child in resource.children.values()
    )


def test_convert_scancode_produces_expected_result(
    scancode_faker: ScanCodeFaker,
) -> None:
    scancode_data = scancode_faker.scancode_data()
    opossum_data = convert_scancode_to_opossum(scancode_data)

    assert opossum_data.review_results is None
    scan_results = opossum_data.scan_results
    assert sum(count_resources(res) for res in scan_results.resources) == len(
        scancode_data.files
    )
    num_attributions = sum(count_attributions(res) for res in scan_results.resources)
    num_license_detections = sum(len(f.license_detections) for f in scancode_data.files)
    assert num_attributions == num_license_detections
