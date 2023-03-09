# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
# SPDX-License-Identifier: Apache-2.0
import pytest


def test_print_hello_world(capsys: pytest.CaptureFixture) -> None:
    print("Hello World")

    captured = capsys.readouterr()
    assert captured.out == "Hello World\n"
