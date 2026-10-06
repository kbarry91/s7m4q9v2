from app.config import (
	get_test_dependency_timeout_seconds,
	is_test_dependency_enabled,
)


def test_test_dependency_is_disabled_by_default(monkeypatch):
	monkeypatch.delenv("TEST_DEPENDENCY_ENABLED", raising=False)

	assert is_test_dependency_enabled() is False


def test_test_dependency_can_be_enabled(monkeypatch):
	monkeypatch.setenv("TEST_DEPENDENCY_ENABLED", "true")

	assert is_test_dependency_enabled() is True


def test_timeout_defaults_to_two_seconds(monkeypatch):
	monkeypatch.delenv("TEST_DEPENDENCY_TIMEOUT_SECONDS", raising=False)

	assert get_test_dependency_timeout_seconds() == 2.0


def test_timeout_can_be_configured(monkeypatch):
	monkeypatch.setenv("TEST_DEPENDENCY_TIMEOUT_SECONDS", "0.5")

	assert get_test_dependency_timeout_seconds() == 0.5
