# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from collections.abc import Sequence
from datetime import datetime
from typing import Any, cast

from faker import Faker, Generator

from opossum_lib.opossum.output_model import OpossumOutputFile
from opossum_lib.opossum_model import Opossum, ScanResults
from tests.opossum_model_generators.opossum_provider import OpossumProvider


class OpossumFaker(Faker):
    opossum_provider: OpossumProvider

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
        self.opossum_provider = OpossumProvider(self)

    def opossum(
        self,
        scan_results: ScanResults | None = None,
        review_results: OpossumOutputFile | None = None,
    ) -> Opossum:
        return self.opossum_provider.opossum(
            scan_results=scan_results, review_results=review_results
        )


def setup_opossum_faker(faker: Faker) -> OpossumFaker:
    faker.add_provider(OpossumProvider)
    faker = cast(OpossumFaker, faker)
    seed = int(datetime.now().timestamp())
    Faker.seed(seed)
    print("\nSeeding faker with ", seed)
    return faker
