#!/usr/bin/env python3

# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0


import logging
from pathlib import Path

import click

from opossum_lib.opossum.file_generation import write_opossum_information_to_file
from opossum_lib.spdx.convert_to_opossum import convert_spdx_to_opossum_information


@click.command()
@click.option(
    "--infile",
    "-i",
    help="The file containing the document to be converted.",
    required=True,
    type=click.Path(exists=True),
)
@click.option(
    "--outfile",
    "-o",
    default="output.opossum",
    show_default=True,
    help="The file path to write the generated opossum document to. The generated file "
    "will be an opossum file, if the specified file path doesn't match this file "
    'extension ".opossum" will be appended.',
)
def spdx2opossum(infile: str, outfile: str) -> None:
    """
    CLI-tool for converting SPDX documents to Opossum documents.
    """
    opossum_information = convert_spdx_to_opossum_information(infile)

    if not outfile.endswith(".opossum"):
        outfile += ".opossum"

    if Path.is_file(Path(outfile)):
        logging.warning(f"{outfile} already exists and will be overwritten.")

    write_opossum_information_to_file(opossum_information, Path(outfile))


if __name__ == "__main__":
    spdx2opossum()
