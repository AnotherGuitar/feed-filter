"""
Pytest configuration and shared fixtures.

This file is automatically loaded by pytest and can contain:
- Shared fixtures used across multiple test files
- Pytest hooks and configuration
- Test utilities and helpers
"""

import pytest

from feed_filter.config import Settings


@pytest.fixture
def test_settings() -> Settings:
    """Provide test settings with safe defaults."""
    return Settings(
        app_name="test-app",
        app_env="testing",
        debug=True,
        log_level="DEBUG",
    )


# Example: Mock external services
# @pytest.fixture
# def mock_api_client(mocker):
#     """Mock API client for testing."""
#     mock = mocker.patch("feed_filter.client.APIClient")
#     mock.return_value.get.return_value = {"status": "ok"}
#     return mock
