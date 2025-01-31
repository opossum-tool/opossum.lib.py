# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Any

from faker.providers import BaseProvider
from faker.providers.misc import Provider as MiscProvider
from faker.providers.person.en_US import Provider as PersonProvider

from opossum_lib.core.entities.source_info import SourceInfo
from tests.shared.generator_helpers import entry_or_none


class SourceInfoProvider(BaseProvider):
    person_provider: PersonProvider
    misc_provider: MiscProvider

    def __init__(self, generator: Any):
        super().__init__(generator)
        self.misc_provider = MiscProvider(generator)
        self.person_provider = PersonProvider(generator)

    def source_info(
        self,
        name: str | None = None,
        document_confidence: int | float | None = None,
        additional_name: str | None = None,
    ) -> SourceInfo:
        return SourceInfo(
            name=name or self.person_provider.name(),
            document_confidence=document_confidence
            or entry_or_none(self.misc_provider, self.random_int(0, 100)),
            additional_name=additional_name
            or entry_or_none(self.misc_provider, self.person_provider.name()),
        )
