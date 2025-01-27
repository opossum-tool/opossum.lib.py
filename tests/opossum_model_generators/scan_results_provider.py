# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Any

from faker.providers import BaseProvider
from faker.providers.file.en_US import Provider as FileProvider
from faker.providers.misc.en_US import Provider as MiscProvider

from opossum_lib.opossum_model import (
    BaseUrlsForSources,
    ExternalAttributionSource,
    FrequentLicense,
    Metadata,
    OpossumPackage,
    Resource,
    ScanResults,
)
from tests.opossum_model_generators.external_attribution_source_provider import (
    ExternalAttributionSourceProvider,
)
from tests.opossum_model_generators.metadata_provider import MetadataProvider
from tests.opossum_model_generators.package_provider import PackageProvider
from tests.opossum_model_generators.resource_provider import ResourceProvider
from tests.test_opossum.generators.helpers import entry_or_none, random_list


class ScanResultsProvider(BaseProvider):
    metadata_provider: MetadataProvider
    package_provider: PackageProvider
    misc_provider: MiscProvider
    external_attribution_source_provider: ExternalAttributionSourceProvider
    file_provider: FileProvider
    resource_provider: ResourceProvider

    def __init__(self, generator: Any) -> None:
        super().__init__(generator)
        self.metadata_provider = MetadataProvider(generator)
        self.package_provider = PackageProvider(generator)
        self.misc_provider = MiscProvider(generator)
        self.external_attribution_source_provider = ExternalAttributionSourceProvider(
            generator
        )
        self.file_provider = FileProvider(generator)
        self.resource_provider = ResourceProvider(generator)

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
            resources=resources or [self.resource_provider.resource_tree()],
            attribution_breakpoints=attribution_breakpoints
            or self.attribution_breakpoints(),
            external_attribution_sources=external_attribution_sources
            or self.external_attribution_source_provider.external_attribution_sources(),
            frequent_licenses=frequent_licenses,
            files_with_children=files_with_children,
            base_urls_for_sources=base_urls_for_sources,
            unassigned_attributions=unassigned_attributions
            or entry_or_none(
                self.misc_provider,
                random_list(
                    self, entry_generator=lambda: self.package_provider.package()
                ),
            ),
        )

    def attribution_breakpoints(self, max_nb_of_breakpoints: int = 5) -> list[str]:
        nb_of_breakpoints = self.random_int(1, max_nb_of_breakpoints)
        return [
            self.file_provider.file_path(extension=[], depth=3)
            for _ in range(nb_of_breakpoints)
        ]
