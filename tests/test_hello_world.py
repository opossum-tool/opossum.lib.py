# SPDX-FileCopyrightText: Meret Behrens
# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>

# SPDX-License-Identifier: Apache-2.0

def test_print_hello_world(capsys):
    print("Hello World")

    captured = capsys.readouterr()
    assert captured.out == "Hello World\n"
