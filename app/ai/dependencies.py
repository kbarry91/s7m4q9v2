"""FastAPI dependency for the Bedrock model client."""

import os

import boto3
from fastapi import HTTPException, status

from app.ai.bedrock_client import BedrockConverseClient
from app.ai.contracts import ModelClient


def get_model_client() -> ModelClient:
    # Build the Bedrock client from environment settings when FastAPI needs it.
    model_id = os.getenv("BEDROCK_MODEL_ID")
    if not model_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The assistant model is not configured",
        )

    runtime_client = boto3.client(
        "bedrock-runtime",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
    )
    return BedrockConverseClient(
        runtime_client=runtime_client,
        model_id=model_id,
        max_tokens=int(os.getenv("BEDROCK_MAX_TOKENS", "512")),
        temperature=float(os.getenv("BEDROCK_TEMPERATURE", "0")),
        timeout_seconds=float(os.getenv("BEDROCK_TIMEOUT_SECONDS", "30")),
    )
