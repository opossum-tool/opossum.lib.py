# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from faker.providers import BaseProvider
from faker.providers.date_time import Provider as DatetimeProvider
from faker.providers.lorem.en_US import Provider as LoremProvider
from faker.providers.misc import Provider as MiscProvider

from opossum_lib.shared.entities.opossum_output_file_model import (
    ManualAttributions,
    Metadata,
    OpossumOutputFileModel,
)
from tests.util.generator_helpers import entry_or_none


class OpossumOutputFileProvider(BaseProvider):
    lorem_provider: LoremProvider
    date_time_provider: DatetimeProvider
    misc_provider: MiscProvider

    def __init__(self, generator: Any):
        super().__init__(generator)
        self.lorem_provider = LoremProvider(generator)
        self.date_time_provider = DatetimeProvider(generator)
        self.misc_provider = MiscProvider(generator)

    def output_file(
        self,
        metadata: Metadata | None = None,
        manual_attributions: dict[str, ManualAttributions] | None = None,
        resources_to_attributions: dict[str, list[str]] | None = None,
        resolved_external_attributions: list[str] | None = None,
    ) -> OpossumOutputFileModel:
        return OpossumOutputFileModel(
            metadata=metadata or self.outfile_metadata(),
            manual_attributions=manual_attributions or {},
            resources_to_attributions=resources_to_attributions or {},
            resolved_external_attributions=resolved_external_attributions,
        )

    def outfile_metadata(
        self,
        project_id: str | None = None,
        file_creation_date: str | None = None,
        input_file_md5_checksum: str | None = None,
    ) -> Metadata:
        return Metadata(
            project_id=project_id or "project-id-" + self.lorem_provider.word(),
            file_creation_date=file_creation_date
            or self.date_time_provider.date_time().isoformat(),
            input_file_md5_checksum=input_file_md5_checksum
            or entry_or_none(self.misc_provider, self.misc_provider.md5()),
        )
