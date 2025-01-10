# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from typing import Any
from unittest import mock

from opossum_lib.opossum.opossum_file import Metadata
from opossum_lib.scancode.convert_scancode_to_opossum import convert_scancode_to_opossum

TEST_SCANCODE_FILE = str(Path(__file__).parent.parent / "data/scancode.json")


@mock.patch("uuid.uuid4", autospec=True, return_value="1234-12345-12345")
def test_create_opossum_metadata(_: Any) -> None:
    result = convert_scancode_to_opossum(TEST_SCANCODE_FILE)

    expected_metadata = Metadata(
        "1234-12345-12345", "2025-01-10T102700.397143", "ScanCode file"
    )

    assert result.metadata == expected_metadata
