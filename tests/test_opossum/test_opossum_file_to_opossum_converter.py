# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
import pytest

from opossum_lib.input_formats.opossum.opossum_file_to_opossum_converter import (
    OpossumFileToOpossumConverter,
)
from opossum_lib.opossum_file_model.opossum_file import (
    OpossumPackage,
    OpossumPackageIdentifier,
)
from tests.test_setup.opossum_file_faker_setup import OpossumFileFaker


class TestOpossumFileToOpossumConverter:
    def test_output_file_moved(self, opossum_file_faker: OpossumFileFaker) -> None:
        output_file = opossum_file_faker.output_file()
        input_file = opossum_file_faker.opossum_file_content(out_file=output_file)

        result = OpossumFileToOpossumConverter.convert_to_opossum(input_file)

        assert result.review_results == output_file

    def test_throws_on_duplicate_attributions(
        self, opossum_file_faker: OpossumFileFaker
    ) -> None:
        external_attributions = self._fake_duplicate_external_attributions(
            opossum_file_faker
        )
        file_information = opossum_file_faker.opossum_file_information(
            external_attributions=external_attributions
        )
        input_file = opossum_file_faker.opossum_file_content(in_file=file_information)

        with pytest.raises(RuntimeError, match=r".*attribution was duplicated.*"):
            OpossumFileToOpossumConverter.convert_to_opossum(input_file)

    @staticmethod
    def _fake_duplicate_external_attributions(
        opossum_file_faker: OpossumFileFaker,
    ) -> dict[OpossumPackageIdentifier, OpossumPackage]:
        external_attributions = opossum_file_faker.external_attributions(
            min_number_of_attributions=2
        )
        package = opossum_file_faker.opossum_package()
        for key in external_attributions:
            external_attributions[key] = package
        return external_attributions
