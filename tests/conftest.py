# SPDX-FileCopyrightText: TNG Technology Consulting GmbH <https://www.tngtech.com>
#
# SPDX-License-Identifier: Apache-2.0

import pytest
from faker.proxy import Faker

from tests.test_setup.opossum_faker_setup import OpossumFaker, setup_opossum_faker
from tests.test_setup.opossum_file_faker_setup import (
    OpossumFileFaker,
    setup_opossum_file_faker,
)


@pytest.fixture
def opossum_file_faker(faker: Faker) -> OpossumFileFaker:
    return setup_opossum_file_faker(faker)


@pytest.fixture
def opossum_faker(faker: Faker) -> OpossumFaker:
    return setup_opossum_faker(faker)
