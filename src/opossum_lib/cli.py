#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0


import logging
import sys
from pathlib import Path

import click
from spdx.model.document import Document as SpdxDocument
from spdx.parser.error import SPDXParsingError
from spdx.parser.parse_anything import parse_file

from opossum_lib.file_generation import generate_json_file_from_tree, write_dict_to_file
from opossum_lib.graph_generation import generate_graph_from_spdx
from opossum_lib.tree_generation import generate_tree_from_graph


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
    help="The file path to write the generated opossum document to. The generated file "
    "will be in JSON format, if the specified file path doesn't match this file "
    'extension ".json" will be appended.',
)
def spdx2opossum(infile: str, outfile: str) -> None:
    """
    CLI-tool for converting SPDX documents to Opossum documents.
    """
    try:
        document: SpdxDocument = parse_file(infile)

    except SPDXParsingError as err:
        log_string = "\n".join(
            ["There have been issues while parsing the provided document:"]
            + [message for message in err.get_messages()]
        )
        logging.error(log_string)
        sys.exit(1)

    graph = generate_graph_from_spdx(document)
    tree = generate_tree_from_graph(graph)

    opossum_information = generate_json_file_from_tree(tree)

    if not outfile.endswith(".json"):
        outfile += ".json"
    write_dict_to_file(opossum_information, Path(outfile))


if __name__ == "__main__":
    spdx2opossum()
