# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Any

from faker.providers import BaseProvider

from opossum_lib.core.entities.opossum import Opossum, ScanResults
from opossum_lib.shared.entities.opossum_output_file import OpossumOutputFile
from tests.opossum_model_generators.scan_results_provider import ScanResultsProvider
from tests.test_opossum.generators.generate_outfile_information import (
    OpossumOutputFileProvider,
)


class OpossumProvider(BaseProvider):
    review_result_provider: OpossumOutputFileProvider
    scan_results_provider: ScanResultsProvider

    def __init__(self, generator: Any):
        super().__init__(generator)
        self.review_result_provider = OpossumOutputFileProvider(generator)
        self.scan_results_provider = ScanResultsProvider(generator)

    def opossum(
        self,
        scan_results: ScanResults | None = None,
        review_results: OpossumOutputFile | None = None,
    ) -> Opossum:
        return Opossum(
            scan_results=scan_results or self.scan_results_provider.scan_results(),
            review_results=review_results or self.review_result_provider.output_file(),
        )
