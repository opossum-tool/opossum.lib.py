# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Sequence
from datetime import datetime
from typing import Any, Literal, cast

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
    SourceInfo,
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

    def opossum_package(
        self,
        source: SourceInfo | None = None,
        attribution_confidence: int | None = None,
        comment: str | None = None,
        package_name: str | None = None,
        package_version: str | None = None,
        package_namespace: str | None = None,
        package_type: str | None = None,
        package_p_u_r_l_appendix: str | None = None,
        copyright: str | None = None,
        license_name: str | None = None,
        license_text: str | None = None,
        url: str | None = None,
        first_party: bool | None = None,
        exclude_from_notice: bool | None = None,
        pre_selected: bool | None = None,
        follow_up: Literal["FOLLOW_UP"] | None = None,
        origin_id: str | None = None,
        origin_ids: list[str] | None = None,
        criticality: Literal["high"] | Literal["medium"] | None = None,
        was_preferred: bool | None = None,
    ) -> OpossumPackage:
        return self.file_information_provider.opossum_package(
            source=source,
            attribution_confidence=attribution_confidence,
            comment=comment,
            package_name=package_name,
            package_version=package_version,
            package_namespace=package_namespace,
            package_type=package_type,
            package_p_u_r_l_appendix=package_p_u_r_l_appendix,
            copyright=copyright,
            license_name=license_name,
            license_text=license_text,
            url=url,
            first_party=first_party,
            exclude_from_notice=exclude_from_notice,
            pre_selected=pre_selected,
            follow_up=follow_up,
            origin_id=origin_id,
            origin_ids=origin_ids,
            criticality=criticality,
            was_preferred=was_preferred,
        )

    def external_attributions(
        self, max_number_of_attributions: int = 50, min_number_of_attributions: int = 5
    ) -> dict[OpossumPackageIdentifier, OpossumPackage]:
        return self.file_information_provider.external_attributions(
            max_number_of_attributions, min_number_of_attributions
        )

    def attribution_breakpoints(self, max_nb_of_breakpoints: int = 5) -> list[str]:
        return self.file_information_provider.attribution_breakpoints(
            max_nb_of_breakpoints
        )

    def external_attribution_source(
        self,
        name: str | None = None,
        priority: int | None = None,
        is_relevant_for_preferred: bool | None = None,
    ) -> ExternalAttributionSource:
        return self.file_information_provider.external_attribution_source(
            name=name,
            priority=priority,
            is_relevant_for_preferred=is_relevant_for_preferred,
        )

    def external_attribution_sources(
        self, max_nb_of_external_attributions: int = 5
    ) -> dict[str, ExternalAttributionSource]:
        return self.file_information_provider.external_attribution_sources(
            max_nb_of_external_attributions
        )


def setup_faker(faker: Faker) -> OpossumFaker:
    faker.add_provider(MetadataProvider)
    faker.add_provider(FileInformationProvider)
    faker = cast(OpossumFaker, faker)
    seed = int(datetime.now().timestamp())
    Faker.seed(seed)
    print("\nSeeding faker with ", seed)
    return faker
