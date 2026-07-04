"""Health check endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel

from app import __version__

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    version: str


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Returns backend liveness. Used by frontend and demo runner."""
    return HealthResponse(status="ok", version=__version__)
