# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Any

from faker.providers import BaseProvider
from faker.providers.date_time import Provider as DatetimeProvider
from faker.providers.lorem.en_US import Provider as LoremProvider
from faker.providers.misc import Provider as MiscProvider

from opossum_lib.core.entities.opossum_model import Metadata
from tests.util.generator_helpers import entry_or_none


class MetadataProvider(BaseProvider):
    lorem_provider: LoremProvider
    date_time_provider: DatetimeProvider
    misc_provider: MiscProvider

    def __init__(self, generator: Any):
        super().__init__(generator)
        self.lorem_provider = LoremProvider(generator)
        self.date_time_provider = DatetimeProvider(generator)
        self.misc_provider = MiscProvider(generator)

    def metadata(
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
            or entry_or_none(self.misc_provider, self.numerify("##.##.##")),
            expected_release_date=expected_release_date
            or entry_or_none(
                self.misc_provider, self.date_time_provider.date_time().isoformat()
            ),
            build_date=build_date
            or entry_or_none(
                self.misc_provider, self.date_time_provider.date_time().isoformat()
            ),
        )
