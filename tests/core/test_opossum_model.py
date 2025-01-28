# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
import json
from copy import deepcopy

from opossum_lib.input_formats.opossum.opossum_file_to_opossum_converter import (
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

        result = OpossumFileToOpossumConverter.convert_to_opossum(opossum_file)

        ## this can change due to the generation of new ids
        result_json = result.model_dump_json()
        expected_result_json = expected_result.model_dump_json()
        result_dict = json.loads(result_json)
        expected_result_dict = json.loads(expected_result_json)
        expected_result_dict["scan_results"]["attribution_to_id"] = None
        result_dict["scan_results"]["attribution_to_id"] = None
        # sort the lists again for comperability
        expected_result_dict["scan_results"]["unassigned_attributions"] = sorted(
            expected_result_dict["scan_results"]["unassigned_attributions"],
            key=lambda x: x["source"]["name"],
        )
        result_dict["scan_results"]["unassigned_attributions"] = sorted(
            result_dict["scan_results"]["unassigned_attributions"],
            key=lambda x: x["source"]["name"],
        )

        assert result_dict == expected_result_dict

    def test_roundtrip_with_resource_ids(self, opossum_faker: OpossumFaker) -> None:
        opossum = opossum_faker.opossum(
            scan_results=opossum_faker.scan_results(generate_attribution_to_id=True)
        )
        expected_result = deepcopy(opossum)

        opossum_file = opossum.to_opossum_file_format()

        result = OpossumFileToOpossumConverter.convert_to_opossum(opossum_file)

        assert result == expected_result
