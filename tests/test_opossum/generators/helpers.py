# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from collections.abc import Callable

from faker.providers import BaseProvider
from faker.providers.misc import Provider as MiscProvider


def entry_or_none[T](
    faker: MiscProvider, entry: T, chance_of_getting_entry: int = 50
) -> T | None:
    if faker.boolean(chance_of_getting_entry):
        return entry
    else:
        return None


def random_list[T](
    faker: BaseProvider,
    entry_generator: Callable[[], T],
    max_number_of_entries: int = 3,
) -> list[T]:
    number_of_entries = faker.random_int(1, max_number_of_entries)
    return [entry_generator() for _ in range(number_of_entries)]
