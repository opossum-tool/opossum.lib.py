# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from collections.abc import Callable
from typing import Any, Literal, cast

from faker.providers import BaseProvider
from faker.providers.date_time import Provider as DatetimeProvider
from faker.providers.file import Provider as FileProvider
from faker.providers.internet import Provider as InternetProvider
from faker.providers.lorem.en_US import Provider as LoremProvider
from faker.providers.misc import Provider as MiscProvider
from faker.providers.person import Provider as PersonProvider

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


def _entry_or_none[T](
    faker: MiscProvider, entry: T, chance_of_getting_entry: int = 50
) -> T | None:
    if faker.boolean(chance_of_getting_entry):
        return entry
    else:
        return None


def _random_list[T](
    faker: BaseProvider,
    entry_generator: Callable[[], T],
    max_number_of_entries: int = 3,
) -> list[T]:
    number_of_entries = faker.random_int(1, max_number_of_entries)
    return [entry_generator() for _ in range(number_of_entries)]


class MetadataProvider(BaseProvider):
    lorem_provider: LoremProvider
    date_time_provider: DatetimeProvider
    misc_provider: MiscProvider

    def __init__(self, generator: Any):
        super().__init__(generator)
        self.lorem_provider = LoremProvider(generator)
        self.date_time_provider = DatetimeProvider(generator)
        self.misc_provider = MiscProvider(generator)

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
        return Metadata(
            project_id=project_id or "project-id-" + self.lorem_provider.word(),
            file_creation_date=file_creation_date
            or self.date_time_provider.date_time().isoformat(),
            project_title=project_title or "project-id-" + self.lorem_provider.word(),
            project_version=project_version
            or _entry_or_none(self.misc_provider, self.numerify("##.##.##")),
            expected_release_date=expected_release_date
            or _entry_or_none(
                self.misc_provider, self.date_time_provider.date_time().isoformat()
            ),
            build_date=build_date
            or _entry_or_none(
                self.misc_provider, self.date_time_provider.date_time().isoformat()
            ),
        )


class FileInformationProvider(BaseProvider):
    metadata_provider: MetadataProvider
    file_provider: FileProvider
    lorem_provider: LoremProvider
    misc_provider: MiscProvider
    person_provider: PersonProvider
    internet_provider: InternetProvider

    def __init__(self, generator: Any):
        super().__init__(generator)
        self.metadata_provider = MetadataProvider(generator)
        self.file_provider = FileProvider(generator)
        self.lorem_provider = LoremProvider(generator)
        self.misc_provider = MiscProvider(generator)
        self.person_provider = PersonProvider(generator)
        self.internet_provider = InternetProvider(generator)

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
        return OpossumInformation(
            metadata=metadata or self.metadata_provider.opossum_input_metadata(),
            resources=resources or self.resource_in_file(),
            external_attributions=external_attributions or self.external_attributions(),
            resources_to_attributions=resources_to_attributions or {},
            attribution_breakpoints=attribution_breakpoints or [],
            external_attribution_sources=external_attribution_sources or {},
            frequent_licenses=frequent_licenses,
            files_with_children=files_with_children,
            base_urls_for_sources=base_urls_for_sources,
        )

    def resource_in_file(
        self,
        depth: int = 3,
        max_folders_per_level: int = 3,
        max_files_per_level: int = 3,
    ) -> ResourceInFile:
        if depth == 0:
            files = self.random_int(0, max_files_per_level)
            return {
                self.file_provider.file_name(category="text"): 1 for _ in range(files)
            }
        else:
            files = self.random_int(0, max_files_per_level)
            file_result = {
                self.file_provider.file_name(category="text"): 1 for _ in range(files)
            }
            folders = self.random_int(0, max_folders_per_level)
            folder_result = {
                self.lorem_provider.word(): self.resource_in_file(
                    depth=depth - 1,
                    max_files_per_level=max_files_per_level,
                    max_folders_per_level=max_folders_per_level,
                )
                for _ in range(folders)
            }
            return {**file_result, **folder_result}

    def source_info(
        self,
        name: str | None = None,
        document_confidence: int | float | None = None,
        additional_name: str | None = None,
    ) -> SourceInfo:
        return SourceInfo(
            name=name or self.person_provider.name(),
            document_confidence=document_confidence
            or _entry_or_none(self.misc_provider, self.random_int(0, 100)),
            additional_name=additional_name
            or _entry_or_none(self.misc_provider, self.person_provider.name()),
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
        return OpossumPackage(
            source=source or self.source_info(),
            attribution_confidence=attribution_confidence
            or _entry_or_none(self.misc_provider, self.random_int()),
            comment=comment
            or _entry_or_none(
                self.misc_provider, self.lorem_provider.paragraph(nb_sentences=5)
            ),
            package_name=package_name
            or _entry_or_none(self.misc_provider, self.person_provider.name()),
            package_version=package_version
            or _entry_or_none(self.misc_provider, self.numerify("##.##.##")),
            package_namespace=package_namespace
            or _entry_or_none(self.misc_provider, self.internet_provider.domain_name()),
            package_type=package_type
            or _entry_or_none(
                self.misc_provider,
                self.lorem_provider.word(ext_word_list=["maven", "github"]),
            ),
            package_p_u_r_l_appendix=package_p_u_r_l_appendix
            or _entry_or_none(
                self.misc_provider, self.lorem_provider.paragraph(nb_sentences=1)
            ),
            copyright=copyright
            or _entry_or_none(
                self.misc_provider, self.lorem_provider.paragraph(nb_sentences=1)
            ),
            license_name=license_name
            or _entry_or_none(self.misc_provider, self.person_provider.name()),
            license_text=license_text
            or _entry_or_none(
                self.misc_provider, self.lorem_provider.paragraph(nb_sentences=10)
            ),
            url=url
            or _entry_or_none(self.misc_provider, self.internet_provider.uri(deep=5)),
            first_party=first_party
            or _entry_or_none(self.misc_provider, self.misc_provider.boolean()),
            exclude_from_notice=exclude_from_notice
            or _entry_or_none(self.misc_provider, self.misc_provider.boolean()),
            pre_selected=pre_selected
            or _entry_or_none(self.misc_provider, self.misc_provider.boolean()),
            follow_up=follow_up or _entry_or_none(self.misc_provider, "FOLLOW_UP"),
            origin_id=origin_id
            or _entry_or_none(self.misc_provider, self.misc_provider.uuid4()),
            origin_ids=origin_ids
            or _random_list(self, cast(Callable[[], str], self.misc_provider.uuid4)),
            criticality=criticality
            or _entry_or_none(
                self.misc_provider,
                self.misc_provider.random_element(["high", "medium"]),
            ),
            was_preferred=was_preferred
            or _entry_or_none(self.misc_provider, self.misc_provider.boolean()),
        )

    def external_attributions(
        self, max_number_of_attributions: int = 10
    ) -> dict[OpossumPackageIdentifier, OpossumPackage]:
        number_of_attributions = self.random_int(0, max_number_of_attributions)
        return {
            cast(str, self.misc_provider.uuid4()): self.opossum_package()
            for _ in range(number_of_attributions)
        }
