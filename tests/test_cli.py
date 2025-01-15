# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
import json
from pathlib import Path
from typing import Any
from zipfile import ZipFile

import pytest
from _pytest.logging import LogCaptureFixture
from click.testing import CliRunner, Result
from spdx_tools.spdx.writer.write_anything import write_file

from opossum_lib.cli import generate
from opossum_lib.opossum.constants import INPUT_JSON_NAME, OUTPUT_JSON_NAME
from tests.test_spdx.helper_methods import _create_minimal_document

test_data_path = Path(__file__).resolve().parent / "data"


def generate_valid_spdx_argument(filename: str = "SPDX.spdx") -> list[str]:
    return ["--spdx", str(test_data_path / filename)]


def generate_valid_opossum_argument(
    filename: str = "opossum_input.opossum",
) -> list[str]:
    return ["--opossum", str(test_data_path / filename)]


def run_with_command_line_arguments(cmd_line_arguments: list[str]) -> Result:
    runner = CliRunner()
    result = runner.invoke(generate, cmd_line_arguments)
    return result


@pytest.mark.parametrize("options", ["--outfile", "-o"])
def test_successful_conversion_of_spdx_file(tmp_path: Path, options: str) -> None:
    result = run_with_command_line_arguments(
        [
            "--spdx",
            str(test_data_path / "SPDX.spdx"),
            options,
            str(tmp_path / "output"),
        ]
    )

    assert result.exit_code == 0

    opossum_dict = read_input_json_from_opossum(str(tmp_path / "output.opossum"))
    expected_opossum_dict = read_json_from_file("expected_opossum.json")

    assert "metadata" in opossum_dict
    # we are using randomly generated UUIDs for the project-id, therefore
    # we need to exclude the "metadata" section from the comparison
    opossum_dict.pop("metadata")
    expected_opossum_dict.pop("metadata")
    assert_expected_file_equals_generated_file(expected_opossum_dict, opossum_dict)


def test_successful_conversion_of_input_only_opossum_file(tmp_path: Path) -> None:
    output_file = str(tmp_path / "output_opossum.opossum")
    result = run_with_command_line_arguments(
        [
            "--opossum",
            str(test_data_path / "opossum_input.opossum"),
            "-o",
            output_file,
        ],
    )

    assert result.exit_code == 0
    expected_opossum_dict = read_json_from_file("opossum_input.json")
    opossum_dict = read_input_json_from_opossum(output_file)

    # Doing individual asserts as otherwise the diff viewer does no longer work
    # in case of errors
    assert result.exit_code == 0
    assert_expected_file_equals_generated_file(expected_opossum_dict, opossum_dict)


def test_successful_conversion_of_input_and_output_opossum_file(tmp_path: Path) -> None:
    output_file = str(tmp_path / "output_opossum.opossum")
    result = run_with_command_line_arguments(
        [
            "--opossum",
            str(test_data_path / "opossum_input_with_result.opossum"),
            "-o",
            output_file,
        ],
    )

    assert result.exit_code == 0

    # Doing individual asserts as otherwise the diff viewer does no longer work
    # in case of errors
    assert_input_json_matches_expectations(output_file)
    assert_output_json_matches_expectations(output_file)


def assert_input_json_matches_expectations(output_file: str) -> None:
    expected_opossum_dict = read_json_from_file("opossum_input.json")
    opossum_dict = read_input_json_from_opossum(output_file)
    assert_expected_file_equals_generated_file(expected_opossum_dict, opossum_dict)


def assert_output_json_matches_expectations(output_file: str) -> None:
    expected_opossum_dict = read_json_from_file("opossum_output.json")
    opossum_dict = read_output_json_from_opossum(output_file)
    assert_expected_file_equals_generated_file(expected_opossum_dict, opossum_dict)


def read_input_json_from_opossum(output_file_path: str) -> Any:
    return read_json_from_zip_file(output_file_path, INPUT_JSON_NAME)


def read_output_json_from_opossum(output_file_path: str) -> Any:
    return read_json_from_zip_file(output_file_path, OUTPUT_JSON_NAME)


def read_json_from_zip_file(output_file_path: str, file_name: str) -> Any:
    with (
        ZipFile(output_file_path, "r") as z,
        z.open(file_name) as file,
    ):
        opossum_dict = json.load(file)
    return opossum_dict


def read_json_from_file(filename: str) -> Any:
    with open(test_data_path / filename, encoding="utf-8") as file:
        expected_opossum_dict = json.load(file)
    return expected_opossum_dict


def assert_expected_file_equals_generated_file(
    expected_opossum_dict: Any, opossum_dict: Any
) -> None:
    assert expected_opossum_dict.keys() == opossum_dict.keys()
    opossum_top_level = expected_opossum_dict.keys()
    for field in opossum_top_level:
        assert opossum_dict.get(field, None) == expected_opossum_dict.get(field, None)


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
        generate_valid_spdx_argument() + generate_valid_spdx_argument(),
        generate_valid_spdx_argument() + generate_valid_opossum_argument(),
        generate_valid_opossum_argument() + generate_valid_opossum_argument(),
    ],
)
def test_cli_with_multiple_files(caplog: LogCaptureFixture, options: list[str]) -> None:
    print(options)
    result = run_with_command_line_arguments(options)
    assert result.exit_code == 1

    assert caplog.messages == ["Merging of multiple files not yet supported!"]


def test_cli_without_inputs(caplog: LogCaptureFixture) -> None:
    result = run_with_command_line_arguments(
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
