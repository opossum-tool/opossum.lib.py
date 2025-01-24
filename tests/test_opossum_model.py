# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from copy import deepcopy

from opossum_lib.opossum.opossum_file_to_opossum_converter import (
    OpossumFileToOpossumConverter,
)
from tests.test_setup.opossum_faker_setup import OpossumFaker


class TestOpossumModelToOpossumFileConversion:
    def test_moves_outfile(self, opossum_faker: OpossumFaker) -> None:
        opossum = opossum_faker.opossum()

        result = opossum.to_opossum_file_format()

        assert result.output_file == opossum.review_results

    def test_roundtrip(self, opossum_faker: OpossumFaker) -> None:
        opossum = opossum_faker.opossum()
        expected_result = deepcopy(opossum)

        opossum_file = opossum.to_opossum_file_format()

        assert opossum_file.input_file

        result = OpossumFileToOpossumConverter.convert_to_opossum(opossum_file)

        assert result.model_dump() == expected_result.model_dump()
