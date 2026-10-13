import pytest
from fastapi import HTTPException

from app.ai.dependencies import get_model_client


def test_model_dependency_requires_bedrock_configuration(monkeypatch):
    monkeypatch.delenv("BEDROCK_MODEL_ID", raising=False)

    with pytest.raises(HTTPException) as error:
        get_model_client()

    assert error.value.status_code == 503
