# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

import sys

import PyInstaller.__main__


def main() -> None:
    executable_name = sys.argv[1]
    PyInstaller.__main__.run(
        [
            "--onefile",
            "--name",
            f"{executable_name}",
            "src/opossum_lib/cli.py",
        ]
    )


if __name__ == "__main__":
    main()
