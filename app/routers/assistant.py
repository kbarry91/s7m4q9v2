"""Conversational assistant endpoint."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.assistant_service import AssistantService
from app.ai.contracts import ModelClient
from app.ai.dependencies import get_model_client
from app.persistence.db import get_session
from app.persistence.repository import ReadingRepository
from app.schemas import AssistantRequest, AssistantResponse
from app.services.query_service import QueryReadingService

router = APIRouter(tags=["assistant"])


@router.post("/assistant", response_model=AssistantResponse)
async def ask_assistant(
    payload: AssistantRequest,
    session: AsyncSession = Depends(get_session),
    model_client: ModelClient = Depends(get_model_client),
) -> AssistantResponse:
    query_service = QueryReadingService(ReadingRepository(session))
    try:
        response = await AssistantService(model_client, query_service).respond(payload.message)
    except TimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The assistant model timed out",
        ) from exc
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The assistant model returned an unusable response",
        ) from exc

    return AssistantResponse(answer=response.text)
