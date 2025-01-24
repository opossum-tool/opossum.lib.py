# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0


import pytest
from _pytest.logging import LogCaptureFixture

from opossum_lib.scancode.convert_scancode_to_opossum import (
    extract_scancode_header,
)
from tests.test_setup.scancode_faker_setup import ScanCodeFaker


def test_extract_scancode_header(scancode_faker: ScanCodeFaker) -> None:
    scancode_data = scancode_faker.scancode_data()
    extracted_header = extract_scancode_header(scancode_data, "test/path/scancode.json")
    assert extracted_header == scancode_data.headers[0]


def test_extract_scancode_header_missing_header(
    caplog: LogCaptureFixture, scancode_faker: ScanCodeFaker
) -> None:
    scancode_data = scancode_faker.scancode_data(headers=[])

    with pytest.raises(SystemExit):
        extract_scancode_header(scancode_data, "test/path/scancode.json")

    assert "header" in caplog.messages[0].lower()


def test_extract_scancode_header_multiple_headers(
    caplog: LogCaptureFixture, scancode_faker: ScanCodeFaker
) -> None:
    header1 = scancode_faker.header()
    header2 = scancode_faker.header()
    scancode_data = scancode_faker.scancode_data(headers=[header1, header2])

    with pytest.raises(SystemExit):
        extract_scancode_header(scancode_data, "test/path/scancode.json")

    assert "header" in caplog.messages[0].lower()
