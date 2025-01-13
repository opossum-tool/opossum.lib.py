#!/usr/bin/env python3

# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0


import logging
import sys
from pathlib import Path

import click

from opossum_lib.opossum.file_generation import write_opossum_information_to_file
from opossum_lib.opossum.opossum_file import OpossumInformation
from opossum_lib.opossum.read_opossum_file import read_opossum_file
from opossum_lib.spdx.convert_to_opossum import convert_spdx_to_opossum_information


@click.group()
def opossum_file() -> None:
    pass


@opossum_file.command()
@click.option(
    "--spdx",
    help="SPDX files used as input.",
    multiple=True,
    type=click.Path(exists=True),
)
@click.option(
    "--opossum",
    help="opossum files used as input.",
    multiple=True,
    type=click.Path(exists=True),
)
@click.option(
    "--outfile",
    "-o",
    default="output.opossum",
    show_default=True,
    help="The file path to write the generated opossum document to. "
    'If appropriate, the extension ".opossum" will be appended.',
)
def generate(spdx: list[str], opossum: list[str], outfile: str) -> None:
    """
    Generate an Opossum file from various other file formats.

    \b
    Currently supported input formats:
      - SPDX
    """
    validate_input_exit_on_error(spdx, opossum)
    opossum_information = convert_after_valid_input(spdx, opossum)

    if not outfile.endswith(".opossum"):
        outfile += ".opossum"

    if Path.is_file(Path(outfile)):
        logging.warning(f"{outfile} already exists and will be overwritten.")

    write_opossum_information_to_file(opossum_information, Path(outfile))


def validate_input_exit_on_error(spdx: list[str], opossum: list[str]) -> None:
    total_number_of_files = len(spdx) + len(opossum)
    if total_number_of_files == 0:
        logging.warning("No input provided. Exiting.")
        sys.exit(1)
    if total_number_of_files > 1:
        logging.error("Merging of multiple files not yet supported!")
        sys.exit(1)


def convert_after_valid_input(
    spdx: list[str], opossum_files: list[str]
) -> OpossumInformation:
    if len(spdx) == 1:
        the_spdx_file = spdx[0]
        return convert_spdx_to_opossum_information(the_spdx_file)
    else:
        opossum_file = opossum_files[0]
        return read_opossum_file(opossum_file)


if __name__ == "__main__":
    opossum_file()
