# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
import json
from pathlib import Path
from zipfile import ZipFile

import pytest
from _pytest.logging import LogCaptureFixture
from click.testing import CliRunner
from spdx_tools.spdx.writer.write_anything import write_file

from opossum_lib.cli import generate
from tests.test_spdx.helper_methods import _create_minimal_document

test_data_path = Path(__file__).resolve().parent / "data"


def generate_valid_spdx_argument(filename: str = "SPDX.spdx") -> str:
    return "--spdx " + str(test_data_path / filename)


def generate_valid_scan_code_argument(filename: str = "scancode.json") -> str:
    return "--scan-code-json " + str(test_data_path / filename)


@pytest.mark.parametrize("options", ["--outfile", "-o"])
def test_cli_with_system_exit_code_0(tmp_path: Path, options: str) -> None:
    runner = CliRunner()

    result = runner.invoke(
        generate,
        [
            "--spdx",
            str(Path(__file__).resolve().parent / "data" / "SPDX.spdx"),
            options,
            str(tmp_path / "output"),
        ],
    )
    with open(
        Path(__file__).resolve().parent / "data" / "expected_opossum.json"
    ) as file:
        expected_opossum_dict = json.load(file)

    assert result.exit_code == 0

    with (
        ZipFile(str(tmp_path / "output.opossum"), "r") as z,
        z.open("input.json") as file,
    ):
        opossum_dict = json.load(file)
    assert "metadata" in opossum_dict
    # we are using randomly generated UUIDs for the project-id, therefore
    # we need to exclude the "metadata" section from the comparison
    opossum_dict.pop("metadata")
    expected_opossum_dict.pop("metadata")
    assert opossum_dict == expected_opossum_dict


def test_cli_no_output_file_provided() -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        file_path = "input.spdx.json"
        create_valid_spdx_document(file_path)
        result = runner.invoke(
            generate,
            "--spdx " + file_path,
        )

        assert result.exit_code == 0

        assert Path.is_file(Path("output.opossum"))


def test_cli_warning_if_outfile_already_exists(caplog: LogCaptureFixture) -> None:
    runner = CliRunner()

    with runner.isolated_filesystem():
        file_path = "input.spdx.json"
        create_valid_spdx_document(file_path)
        with open("output.opossum", "w") as f:
            f.write("")
        result = runner.invoke(
            generate,
            "--spdx " + file_path + " -o output.opossum",
        )

    assert result.exit_code == 0

    assert caplog.messages == ["output.opossum already exists and will be overwritten."]


def test_cli_with_system_exit_code_1() -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("invalid_spdx.spdx", "w") as f:
            f.write("SPDXID: SPDXRef-DOCUMENT")
        result = runner.invoke(generate, "--spdx invalid_spdx.spdx -o invalid")

    assert result.exit_code == 1


def test_cli_with_invalid_document(caplog: LogCaptureFixture) -> None:
    runner = CliRunner()
    with runner.isolated_filesystem():
        create_invalid_spdx_document("invalid_spdx.spdx")
        result = runner.invoke(generate, "--spdx invalid_spdx.spdx -o invalid")

    assert result.output == ""
    assert caplog.messages == [
        "The given SPDX document is not valid, this might cause issues with "
        "the conversion."
    ]


@pytest.mark.parametrize(
    "options",
    [
        generate_valid_spdx_argument() + " " + generate_valid_spdx_argument(),
        generate_valid_spdx_argument() + " " + generate_valid_scan_code_argument(),
        generate_valid_scan_code_argument() + " " + generate_valid_scan_code_argument(),
    ],
)
def test_cli_with_multiple_files(caplog: LogCaptureFixture, options: str) -> None:
    runner = CliRunner()

    result = runner.invoke(generate, options)
    assert result.exit_code == 1

    assert caplog.messages == ["Merging of multiple files not yet supported!"]


def test_cli_without_inputs(caplog: LogCaptureFixture) -> None:
    runner = CliRunner()

    result = runner.invoke(
        generate,
        [
            "-o",
            "output.opossum",
        ],
    )
    assert result.exit_code == 1

    assert caplog.messages == ["No input provided. Exiting."]


def create_invalid_spdx_document(file_path: str) -> None:
    document = _create_minimal_document()
    document.creation_info.spdx_id = "DocumentID"

    write_file(document, file_path, False)


def create_valid_spdx_document(file_path: str) -> None:
    document = _create_minimal_document()
    write_file(document, file_path, False)
