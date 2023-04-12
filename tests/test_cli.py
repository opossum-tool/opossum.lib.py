# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
import json
from pathlib import Path
from typing import Tuple

import pytest
from click.testing import CliRunner

from opossum_lib.cli import spdx2opossum


@pytest.mark.parametrize("options", [("--infile", "--outfile"), ("-i", "-o")])
def test_cli(tmp_path: Path, options: Tuple[str, str]) -> None:
    runner = CliRunner()

    result = runner.invoke(
        spdx2opossum,
        [
            options[0],
            str(Path(__file__).resolve().parent / "data" / "SPDX.spdx"),
            options[1],
            str(tmp_path / "output"),
        ],
    )

    assert result.exit_code == 0

    with open(tmp_path / "output.json") as file:
        opossum_dict = json.load(file)
    assert "metadata" in opossum_dict
