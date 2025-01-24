# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Any

from faker.providers import BaseProvider

from opossum_lib.opossum_model import (
    BaseUrlsForSources,
    ExternalAttributionSource,
    FrequentLicense,
    Metadata,
    OpossumPackage,
    Resource,
    ScanResults,
)
from tests.opossum_model_generators.metadata_provider import MetadataProvider


class ScanResultsProvider(BaseProvider):
    metadata_provider: MetadataProvider

    def __init__(self, generator: Any) -> None:
        super().__init__(generator)
        self.metadata_provider = MetadataProvider(generator)

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
        attribution_to_id: dict[OpossumPackage, str] | None = None,
        unassigned_attributions: list[OpossumPackage] | None = None,
    ) -> ScanResults:
        return ScanResults(
            metadata=metadata or self.metadata_provider.metadata(),
            resources=resources or [],
            attribution_breakpoints=attribution_breakpoints or [],
            external_attribution_sources=external_attribution_sources or {},
            frequent_licenses=frequent_licenses,
            files_with_children=files_with_children,
            base_urls_for_sources=base_urls_for_sources,
            attribution_to_id=attribution_to_id or {},
            unassigned_attributions=unassigned_attributions or None,
        )
