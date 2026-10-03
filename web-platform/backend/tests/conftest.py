import os

import pytest


@pytest.fixture
def postgres_url() -> str:
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for integration tests")
    return url
