# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from collections.abc import Callable
from typing import Any, Literal, cast

from faker.providers import BaseProvider
from faker.providers.internet.en_US import Provider as InternetProvider
from faker.providers.lorem.en_US import Provider as LoremProvider
from faker.providers.misc.en_US import Provider as MiscProvider
from faker.providers.person.en_US import Provider as PersonProvider

from opossum_lib.core.entities.opossum_model import OpossumPackage, SourceInfo
from tests.opossum_model_generators.source_info_provider import SourceInfoProvider
from tests.util.generator_helpers import entry_or_none, random_list


class PackageProvider(BaseProvider):
    source_info_provider: SourceInfoProvider
    misc_provider: MiscProvider
    lorem_provider: LoremProvider
    person_provider: PersonProvider
    internet_provider: InternetProvider

    def __init__(self, generator: Any):
        super().__init__(generator)
        self.source_info_provider = SourceInfoProvider(generator)
        self.misc_provider = MiscProvider(generator)
        self.lorem_provider = LoremProvider(generator)
        self.person_provider = PersonProvider(generator)
        self.internet_provider = InternetProvider(generator)

    def package(
        self,
        source: SourceInfo | None = None,
        attribution_confidence: int | None = None,
        comment: str | None = None,
        package_name: str | None = None,
        package_version: str | None = None,
        package_namespace: str | None = None,
        package_type: str | None = None,
        package_purl_appendix: str | None = None,
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
            source=source or self.source_info_provider.source_info(),
            attribution_confidence=attribution_confidence
            or entry_or_none(self.misc_provider, self.random_int()),
            comment=comment
            or entry_or_none(
                self.misc_provider, self.lorem_provider.paragraph(nb_sentences=5)
            ),
            package_name=package_name
            or entry_or_none(self.misc_provider, self.person_provider.name()),
            package_version=package_version
            or entry_or_none(self.misc_provider, self.numerify("##.##.##")),
            package_namespace=package_namespace
            or entry_or_none(self.misc_provider, self.internet_provider.domain_name()),
            package_type=package_type
            or entry_or_none(
                self.misc_provider,
                self.lorem_provider.word(ext_word_list=["maven", "github"]),
            ),
            package_purl_appendix=package_purl_appendix
            or entry_or_none(
                self.misc_provider, self.lorem_provider.paragraph(nb_sentences=1)
            ),
            copyright=copyright
            or entry_or_none(
                self.misc_provider, self.lorem_provider.paragraph(nb_sentences=1)
            ),
            license_name=license_name
            or entry_or_none(self.misc_provider, self.person_provider.name()),
            license_text=license_text
            or entry_or_none(
                self.misc_provider, self.lorem_provider.paragraph(nb_sentences=10)
            ),
            url=url
            or entry_or_none(self.misc_provider, self.internet_provider.uri(deep=5)),
            first_party=first_party
            or entry_or_none(self.misc_provider, self.misc_provider.boolean()),
            exclude_from_notice=exclude_from_notice
            or entry_or_none(self.misc_provider, self.misc_provider.boolean()),
            pre_selected=pre_selected
            or entry_or_none(self.misc_provider, self.misc_provider.boolean()),
            follow_up=follow_up or entry_or_none(self.misc_provider, "FOLLOW_UP"),
            origin_id=origin_id
            or entry_or_none(self.misc_provider, self.misc_provider.uuid4()),
            origin_ids=origin_ids
            or random_list(self, cast(Callable[[], str], self.misc_provider.uuid4)),
            criticality=criticality
            or entry_or_none(
                self.misc_provider,
                self.misc_provider.random_element(["high", "medium"]),
            ),
            was_preferred=was_preferred
            or entry_or_none(self.misc_provider, self.misc_provider.boolean()),
        )
