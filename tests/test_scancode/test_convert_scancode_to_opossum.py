# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

import json
from pathlib import Path
from typing import Any
from unittest import mock

import pytest
from _pytest.logging import LogCaptureFixture

from opossum_lib.opossum.opossum_file import Metadata
from opossum_lib.scancode.convert_scancode_to_opossum import (
    convert_scancode_to_opossum,
    create_opossum_metadata,
)
from opossum_lib.scancode.model import ScanCodeData

TEST_SCANCODE_FILE = str(Path(__file__).parent.parent / "data/scancode.json")


@mock.patch("uuid.uuid4", autospec=True, return_value="1234-12345-12345")
def test_create_opossum_metadata(_: Any) -> None:
    result = convert_scancode_to_opossum(TEST_SCANCODE_FILE)

    expected_metadata = Metadata(
        "1234-12345-12345", "2025-01-10T102700.397143", "ScanCode file"
    )

    assert result.metadata == expected_metadata


def test_create_opossum_metadata_missing_header(caplog: LogCaptureFixture) -> None:
    scancode_data = _create_valid_scancode_data()
    scancode_data.headers = []

    with pytest.raises(SystemExit):
        create_opossum_metadata(scancode_data)

    assert "missing the header" in caplog.messages[0]


def test_create_opossum_metadata_multiple_headers(caplog: LogCaptureFixture) -> None:
    scancode_data = _create_valid_scancode_data()
    scancode_data.headers.append(scancode_data.headers[0])

    with pytest.raises(SystemExit):
        create_opossum_metadata(scancode_data)

    assert "has 2 headers" in caplog.messages[0]


def _create_valid_scancode_data() -> ScanCodeData:
    with open(TEST_SCANCODE_FILE) as inp:
        json_data = json.load(inp)
    return ScanCodeData.model_validate(json_data)
