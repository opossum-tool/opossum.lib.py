#  SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#  #
#  SPDX-License-Identifier: Apache-2.0
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

import pytest
from _pytest.logging import LogCaptureFixture

from opossum_lib.input_formats.opossum.services.opossum_file_reader import (
    OpossumFileReader,
)

TEST_DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"


class TestOpossumFileReader:
    def test_read_corrupted_file_exits_1(self, caplog: LogCaptureFixture) -> None:
        input_path = TEST_DATA_DIR / "opossum_input_corrupt.opossum"
        opossum_format_reader = OpossumFileReader(input_path)

        with pytest.raises(SystemExit) as system_exit:
            opossum_format_reader.read()
        assert system_exit.value.code == 1
        assert "is corrupt and does not contain 'input.json'" in caplog.messages[0]

    def test_read_with_output_json(self) -> None:
        input_path = TEST_DATA_DIR / "opossum_input_with_result.opossum"
        opossum_format_reader = OpossumFileReader(input_path)

        result = opossum_format_reader.read()

        assert result is not None
        assert result.scan_results is not None
        assert result.review_results is not None
