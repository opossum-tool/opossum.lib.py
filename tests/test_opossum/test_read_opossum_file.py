# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path

import pytest
from _pytest.logging import LogCaptureFixture

from opossum_lib.opossum.read_opossum_file import read_opossum_file

TEST_DATA_PATH = Path(__file__).resolve().parent.parent / "data"


def test_read_opossum_file_corrupted_file_exits_1(caplog: LogCaptureFixture) -> None:
    input_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "opossum_input_corrupt.opossum"
    )

    with pytest.raises(SystemExit) as system_exit:
        read_opossum_file(str(input_path))
    assert system_exit.value.code == 1
    assert "is corrupt and does not contain 'input.json'" in caplog.messages[0]
