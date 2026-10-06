import os


def is_test_dependency_enabled() -> bool:
    return os.getenv("TEST_DEPENDENCY_ENABLED", "false").lower() == "true"

def get_test_dependency_timeout_seconds() -> float:
    return float(os.getenv("TEST_DEPENDENCY_TIMEOUT_SECONDS", "2"))