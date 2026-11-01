"""Local web UI. Run with: python -m uvicorn main:app --reload"""

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    OpenAIError,
    RateLimitError,
)
from pydantic import BaseModel, ConfigDict, Field

from app.classifier import classify_ticket
from app.schemas import TriageResult


STATIC_DIR = Path(__file__).resolve().parent / "static"
app = FastAPI(
    title="AI Ticket Triage API",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class TicketRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    message: str = Field(min_length=1, max_length=10000)


class TokenUsage(BaseModel):
    input_tokens: int
    output_tokens: int
    total_tokens: int


class TicketResponse(BaseModel):
    ticket: str
    classification: TriageResult
    usage: TokenUsage | None = None


@app.get("/", response_class=FileResponse, include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health_check():
    """Check the web server without making a model request."""
    return {"status": "ok"}


@app.post("/classify", response_model=TicketResponse)
def classify_ticket_endpoint(ticket: TicketRequest):
    if not os.getenv("OPENAI_API_KEY", "").strip():
        raise HTTPException(
            status_code=503,
            detail="Set OPENAI_API_KEY in your .env file and restart the server.",
        )

    try:
        result, usage = classify_ticket(ticket.message)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=503,
            detail="OpenAI authentication failed. Check OPENAI_API_KEY on the server.",
        ) from exc
    except RateLimitError as exc:
        raise HTTPException(
            status_code=503,
            detail="OpenAI rate limit or quota reached. Check your usage and try again later.",
        ) from exc
    except APITimeoutError as exc:
        raise HTTPException(
            status_code=504,
            detail="Classification timed out. Please try again.",
        ) from exc
    except APIConnectionError as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not reach OpenAI. Check the server's internet connection.",
        ) from exc
    except (OpenAIError, RuntimeError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Classification failed. Check the server's OpenAI configuration and try again.",
        ) from exc

    return TicketResponse(
        ticket=ticket.message,
        classification=result,
        usage=TokenUsage.model_validate(usage, from_attributes=True) if usage else None,
    )
