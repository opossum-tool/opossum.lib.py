# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Any

from faker.providers import BaseProvider
from faker.providers.misc import Provider as MiscProvider
from faker.providers.person import Provider as PersonProvider

from opossum_lib.core.entities.opossum import ExternalAttributionSource
from tests.util.generator_helpers import entry_or_none


class ExternalAttributionSourceProvider(BaseProvider):
    person_provider: PersonProvider
    misc_provider: MiscProvider

    def __init__(self, generator: Any):
        super().__init__(generator)
        self.person_provider = PersonProvider(generator)
        self.misc_provider = MiscProvider(generator)

    def external_attribution_source(
        self,
        name: str | None = None,
        priority: int | None = None,
        is_relevant_for_preferred: bool | None = None,
    ) -> ExternalAttributionSource:
        return ExternalAttributionSource(
            name=name or self.person_provider.name(),
            priority=priority or self.random_int(1, 100),
            is_relevant_for_preferred=is_relevant_for_preferred
            or entry_or_none(self.misc_provider, self.misc_provider.boolean()),
        )

    def external_attribution_sources(
        self, max_nb_of_external_attributions: int = 5
    ) -> dict[str, ExternalAttributionSource]:
        nb_of_external_attributions = self.random_int(
            1, max_nb_of_external_attributions
        )
        return {
            self.person_provider.first_name(): self.external_attribution_source()
            for _ in range(nb_of_external_attributions)
        }
