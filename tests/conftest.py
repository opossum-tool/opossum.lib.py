import pytest
from faker.proxy import Faker

from tests.test_setup.faker_setup import OpossumFaker, setup_faker


@pytest.fixture
def opossum_faker(faker: Faker) -> OpossumFaker:
    return setup_faker(faker)
