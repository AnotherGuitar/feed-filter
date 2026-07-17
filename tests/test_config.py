"""Tests for configuration management."""

from feed_filter.config import Settings


def test_settings_defaults():
    """Test that settings have sensible defaults."""
    settings = Settings()
    assert settings.app_name == "feed-filter"
    assert settings.app_env == "development"
    assert settings.debug is True
    assert settings.log_level == "INFO"


def test_settings_from_env(monkeypatch):
    """Test that settings can be loaded from environment variables."""
    monkeypatch.setenv("APP_NAME", "test-app")
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")

    settings = Settings()
    assert settings.app_name == "test-app"
    assert settings.app_env == "production"
    assert settings.debug is False
    assert settings.log_level == "WARNING"


def test_is_production():
    """Test production environment detection."""
    settings = Settings(app_env="production")
    assert settings.is_production is True
    assert settings.is_development is False


def test_is_development():
    """Test development environment detection."""
    settings = Settings(app_env="development")
    assert settings.is_production is False
    assert settings.is_development is True


def test_settings_case_insensitive(monkeypatch):
    """Test that environment variables are case insensitive."""
    monkeypatch.setenv("APP_NAME", "test-app")
    monkeypatch.setenv("app_name", "test-app-lowercase")

    settings = Settings()
    # Should accept either case
    assert settings.app_name in ["test-app", "test-app-lowercase"]
