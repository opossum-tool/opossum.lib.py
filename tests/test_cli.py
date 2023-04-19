# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
import json
from pathlib import Path
from typing import Tuple

import pytest
from _pytest.logging import LogCaptureFixture
from click.testing import CliRunner
from spdx.writer.tagvalue.tagvalue_writer import write_document_to_file

from opossum_lib.cli import spdx2opossum
from tests.helper_methods import _create_minimal_document


@pytest.mark.parametrize("options", [("--infile", "--outfile"), ("-i", "-o")])
def test_cli_with_system_exit_code_0(tmp_path: Path, options: Tuple[str, str]) -> None:
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


def test_cli_with_system_exit_code_1() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("invalid_spdx.spdx", "w") as f:
            f.write("SPDXID: SPDXRef-DOCUMENT")
        result = runner.invoke(spdx2opossum, "-i invalid_spdx.spdx -o invalid")

    assert result.exit_code == 1


def test_cli_with_invalid_document(caplog: LogCaptureFixture) -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        create_invalid_spdx_document("invalid_spdx.spdx")
        result = runner.invoke(spdx2opossum, "-i invalid_spdx.spdx -o invalid")

    assert result.output == ""
    assert caplog.messages == [
        "The given SPDX document is not valid, this might cause issues with "
        "the conversion."
    ]


def create_invalid_spdx_document(file_path: str) -> None:
    document = _create_minimal_document()
    document.creation_info.spdx_id = "DocumentID"

    write_document_to_file(document, file_path, False)
