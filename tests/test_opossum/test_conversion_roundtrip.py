# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from copy import deepcopy

from test_setup.opossum_file_faker_setup import OpossumFileFaker

from opossum_lib.opossum.opossum_file_content import OpossumFileContent
from opossum_lib.opossum.opossum_file_to_opossum_converter import (
    OpossumFileToOpossumConverter,
)


class TestConversionRoundtrip:
    def test_roundtrip(self, opossum_file_faker: OpossumFileFaker) -> None:
        start_file_content = opossum_file_faker.opossum_file_content()
        TestConversionRoundtrip._check_round_trip(start_file_content)

    def test_input_file_only(self, opossum_file_faker: OpossumFileFaker) -> None:
        start_file_content = OpossumFileContent(input_file=opossum_file_faker.opossum_file_information())
        TestConversionRoundtrip._check_round_trip(start_file_content)

    def test_surplus_attributions(self, opossum_file_faker: OpossumFileFaker) -> None:
        start_file_content = opossum_file_faker.opossum_file_content()
        start_file_content.input_file.external_attributions.update(opossum_file_faker.external_attributions())
        TestConversionRoundtrip._check_round_trip(start_file_content)


    @staticmethod
    def _check_round_trip(start_file_content):
        expected_file_content = deepcopy(start_file_content)
        result = OpossumFileToOpossumConverter.convert_to_opossum(
            start_file_content
        ).to_opossum_file_format()
        assert result == expected_file_content