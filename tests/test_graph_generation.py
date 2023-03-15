# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
import os

from spdx.parser.parse_anything import parse_file

from opossum_lib.generate_graph_from_spdx_lite import generate_graph_from_spdx_lite


def test_generate_graph_from_spdx_lite() -> None:
    document = parse_file(
        os.path.join(os.path.dirname(__file__), "./data/SPDXLite.spdx")
    )

    graph = generate_graph_from_spdx_lite(document)

    assert document.creation_info.spdx_id in graph.nodes()
    assert graph.number_of_nodes() == 4
    assert len(graph.edges()) == 3
