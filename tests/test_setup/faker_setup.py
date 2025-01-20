# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Sequence
from typing import Any, cast

from faker import Faker, Generator

from opossum_lib.opossum.opossum_file import (
    BaseUrlsForSources,
    ExternalAttributionSource,
    FrequentLicense,
    Metadata,
    OpossumInformation,
    OpossumPackage,
    OpossumPackageIdentifier,
    ResourceInFile,
    ResourcePath,
)
from tests.test_opossum.generators.generate_file_information import (
    FileInformationProvider,
    MetadataProvider,
)


class OpossumFaker(Faker):
    file_information_provider: FileInformationProvider
    metadata_provider: MetadataProvider

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
        self.file_information_provider = FileInformationProvider(self)
        self.metadata_provider = MetadataProvider(self)

    def opossum_file_information(
        self,
        *,
        metadata: Metadata | None = None,
        resources: ResourceInFile | None = None,
        external_attributions: dict[OpossumPackageIdentifier, OpossumPackage]
        | None = None,
        resources_to_attributions: dict[ResourcePath, list[OpossumPackageIdentifier]]
        | None = None,
        attribution_breakpoints: list[str] | None = None,
        external_attribution_sources: dict[str, ExternalAttributionSource]
        | None = None,
        frequent_licenses: list[FrequentLicense] | None = None,
        files_with_children: list[str] | None = None,
        base_urls_for_sources: BaseUrlsForSources | None = None,
    ) -> OpossumInformation:
        return self.file_information_provider.opossum_file_information(
            metadata=metadata,
            resources=resources,
            external_attributions=external_attributions,
            resources_to_attributions=resources_to_attributions,
            attribution_breakpoints=attribution_breakpoints,
            external_attribution_sources=external_attribution_sources,
            frequent_licenses=frequent_licenses,
            files_with_children=files_with_children,
            base_urls_for_sources=base_urls_for_sources,
        )

    def opossum_input_metadata(
        self,
        *,
        project_id: str | None = None,
        file_creation_date: str | None = None,
        project_title: str | None = None,
        project_version: str | None = None,
        expected_release_date: str | None = None,
        build_date: str | None = None,
    ) -> Metadata:
        return self.metadata_provider.opossum_input_metadata(
            project_id=project_id,
            file_creation_date=file_creation_date,
            project_title=project_title,
            project_version=project_version,
            expected_release_date=expected_release_date,
            build_date=build_date,
        )


def setup_faker(faker: Faker) -> OpossumFaker:
    faker.add_provider(MetadataProvider)
    faker.add_provider(FileInformationProvider)
    faker = cast(OpossumFaker, faker)
    return faker
