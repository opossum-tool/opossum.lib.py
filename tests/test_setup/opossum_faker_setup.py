# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from collections.abc import Sequence
from datetime import datetime
from typing import Any, cast

from faker import Faker, Generator

from opossum_lib.opossum.output_model import OpossumOutputFile
from opossum_lib.opossum_model import (
    BaseUrlsForSources,
    ExternalAttributionSource,
    FrequentLicense,
    Metadata,
    Opossum,
    OpossumPackage,
    Resource,
    ScanResults,
)
from tests.opossum_model_generators.opossum_provider import OpossumProvider
from tests.opossum_model_generators.scan_results_provider import ScanResultsProvider


class OpossumFaker(Faker):
    opossum_provider: OpossumProvider
    scan_results_provider: ScanResultsProvider

    def __init__(
        self,
        locale: str | Sequence[str] | dict[str, int | float] | None = None,
        providers: list[str] | None = None,
        generator: Generator | None = None,
        includes: list[str] | None = None,
        use_weighting: bool = True,
        **config: Any,
    ):
        super().__init__(
            locale, providers, generator, includes, use_weighting, **config
        )
        self.opossum_provider = OpossumProvider(self)
        self.scan_results_provider = ScanResultsProvider(self)

    def opossum(
        self,
        scan_results: ScanResults | None = None,
        review_results: OpossumOutputFile | None = None,
    ) -> Opossum:
        return self.opossum_provider.opossum(
            scan_results=scan_results, review_results=review_results
        )

    def scan_results(
        self,
        metadata: Metadata | None = None,
        resources: list[Resource] | None = None,
        attribution_breakpoints: list[str] | None = None,
        external_attribution_sources: dict[str, ExternalAttributionSource]
        | None = None,
        frequent_licenses: list[FrequentLicense] | None = None,
        files_with_children: list[str] | None = None,
        base_urls_for_sources: BaseUrlsForSources | None = None,
        generate_attribution_to_id: bool = False,
        unassigned_attributions: list[OpossumPackage] | None = None,
    ) -> ScanResults:
        return self.scan_results_provider.scan_results(
            metadata=metadata,
            resources=resources,
            attribution_breakpoints=attribution_breakpoints,
            external_attribution_sources=external_attribution_sources,
            frequent_licenses=frequent_licenses,
            files_with_children=files_with_children,
            base_urls_for_sources=base_urls_for_sources,
            generate_attribution_to_id=generate_attribution_to_id,
            unassigned_attributions=unassigned_attributions,
        )


def setup_opossum_faker(faker: Faker) -> OpossumFaker:
    faker.add_provider(OpossumProvider)
    faker.add_provider(ScanResultsProvider)
    faker = cast(OpossumFaker, faker)
    seed = int(datetime.now().timestamp())
    Faker.seed(seed)
    print("\nSeeding faker with ", seed)
    return faker
