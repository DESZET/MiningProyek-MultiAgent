"""Error response schema — mirrors API.md §5.6."""

from typing import Optional

from pydantic import BaseModel


class ApiError(BaseModel):
    detail: str
    code: Optional[str] = None
