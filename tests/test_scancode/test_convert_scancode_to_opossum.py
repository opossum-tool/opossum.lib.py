# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

import json
from pathlib import Path

import pytest
from _pytest.logging import LogCaptureFixture

from opossum_lib.scancode.convert_scancode_to_opossum import (
    extract_scancode_header,
)
from opossum_lib.scancode.model import ScanCodeData

TEST_SCANCODE_FILE = str(Path(__file__).parent.parent / "data/scancode_input.json")


def test_extract_scancode_header() -> None:
    scancode_data = _create_valid_scancode_data()
    extracted_header = extract_scancode_header(scancode_data, "test/path/scancode.json")
    assert extracted_header == scancode_data.headers[0]


def test_extract_scancode_header_missing_header(caplog: LogCaptureFixture) -> None:
    scancode_data = _create_valid_scancode_data()
    scancode_data.headers = []

    with pytest.raises(SystemExit):
        extract_scancode_header(scancode_data, "test/path/scancode.json")

    assert "header" in caplog.messages[0].lower()


def test_extract_scancode_header_multiple_headers(caplog: LogCaptureFixture) -> None:
    scancode_data = _create_valid_scancode_data()
    scancode_data.headers.append(scancode_data.headers[0])

    with pytest.raises(SystemExit):
        extract_scancode_header(scancode_data, "test/path/scancode.json")

    assert "header" in caplog.messages[0].lower()


def _create_valid_scancode_data() -> ScanCodeData:
    with open(TEST_SCANCODE_FILE) as inp:
        json_data = json.load(inp)
    return ScanCodeData.model_validate(json_data)
