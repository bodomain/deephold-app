"""Pytest fixtures."""

import pytest

from deephold_api.models import init_app_schema


@pytest.fixture(autouse=True, scope="session")
def create_schema():
    """Create app schema + tables before tests run."""
    init_app_schema()
    yield
