# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

import json
from pathlib import Path
from unittest import mock

import pytest
from _pytest.logging import LogCaptureFixture

from opossum_lib.opossum.opossum_file import Metadata
from opossum_lib.scancode.convert_scancode_to_opossum import (
    create_opossum_metadata,
    validate_scancode_json,
)
from opossum_lib.scancode.model import ScanCodeData

TEST_SCANCODE_FILE = str(Path(__file__).parent.parent / "data/scancode_input.json")


def test_create_opossum_metadata() -> None:
    scancode_data = _create_valid_scancode_data()
    with mock.patch("uuid.uuid4", return_value="1234-12345-12345"):
        metadata = create_opossum_metadata(scancode_data)

    expected_metadata = Metadata(
        projectId="1234-12345-12345",
        fileCreationDate="2025-01-10T102700.397143",
        projectTitle="ScanCode file",
    )

    assert metadata == expected_metadata


def test_load_scancode_json_missing_header(caplog: LogCaptureFixture) -> None:
    scancode_data = _create_valid_scancode_data()
    scancode_data.headers = []

    with pytest.raises(SystemExit):
        validate_scancode_json(scancode_data, "test/path/scancode.json")

    assert "header" in caplog.messages[0].lower()


def test_validate_scancode_json_multiple_headers(caplog: LogCaptureFixture) -> None:
    scancode_data = _create_valid_scancode_data()
    scancode_data.headers.append(scancode_data.headers[0])

    with pytest.raises(SystemExit):
        validate_scancode_json(scancode_data, "test/path/scancode.json")

    assert "header" in caplog.messages[0].lower()


def _create_valid_scancode_data() -> ScanCodeData:
    with open(TEST_SCANCODE_FILE) as inp:
        json_data = json.load(inp)
    return ScanCodeData.model_validate(json_data)
