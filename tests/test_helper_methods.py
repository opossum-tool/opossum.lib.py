# SPDX-FileCopyrightText: 2023 TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0
from functools import reduce

from opossum_lib.helper_methods import _merge_nested_dicts


def test_merge_nested_dicts() -> None:
    list_of_dicts = [{"A": 1}, {"A": {"B": {"C": 1}}}, {"A": {"B": 1}}, {"A": {"D": 1}}]

    merged_dict = reduce(
        lambda dict1, dict2: _merge_nested_dicts(dict1, dict2), list_of_dicts  # type: ignore # noqa
    )

    assert merged_dict == {"A": {"B": {"C": 1}, "D": 1}}
