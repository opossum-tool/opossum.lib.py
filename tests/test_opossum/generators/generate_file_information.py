# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Any

from faker.providers import BaseProvider
from faker.providers.date_time import Provider as DatetimeProvider
from faker.providers.file import Provider as FileProvider
from faker.providers.lorem.en_US import Provider as LoremProvider
from faker.providers.misc import Provider as MiscProvider

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


def _entry_or_none[T](
    faker: MiscProvider, entry: T, chance_of_getting_entry: int = 50
) -> T | None:
    if faker.boolean(chance_of_getting_entry):
        return entry
    else:
        return None


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

    def __init__(self, generator: Any):
        super().__init__(generator)
        self.metadata_provider = MetadataProvider(generator)
        self.file_provider = FileProvider(generator)
        self.lorem_provider = LoremProvider(generator)

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
            external_attributions=external_attributions or {},
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
