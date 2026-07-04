"""ApiException + error code constants.

The single error type that services raise. The global exception handler in
main.py catches these and formats them as the JSON envelope described in
API.md §2 ({ "detail": "...", "code": "..." }).
"""

from fastapi import HTTPException


class ApiException(HTTPException):
    """Raised by services to signal a structured error.

    Attributes:
        status_code: HTTP status code
        code: machine-readable error code (e.g., "MATERIAL_TOO_SHORT")
        detail: human-readable message in Indonesian, safe to display
    """

    def __init__(self, status_code: int, code: str, detail: str):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code


# ============================================================================
# Error code constants (mirror API.md §6)
# Use these instead of string literals to avoid typos.
# ============================================================================

# Generic
INTERNAL_ERROR = "INTERNAL_ERROR"

# Auth (POST /auth/google) — Google login via Google Identity Services
AUTH_UNAVAILABLE = "AUTH_UNAVAILABLE"          # GOOGLE_CLIENT_ID or DB not configured / DB down
INVALID_GOOGLE_TOKEN = "INVALID_GOOGLE_TOKEN"  # credential failed Google verification

# Material input (POST /quiz/generate)
MATERIAL_EMPTY = "MATERIAL_EMPTY"
MATERIAL_TOO_SHORT = "MATERIAL_TOO_SHORT"
MATERIAL_TOO_LONG = "MATERIAL_TOO_LONG"
MATERIAL_LOW_QUALITY = "MATERIAL_LOW_QUALITY"  # unsuitable material (CV/English/list)
QUIZ_GENERATION_FAILED = "QUIZ_GENERATION_FAILED"

# Quiz submission (POST /quiz/submit)
QUIZ_NOT_FOUND = "QUIZ_NOT_FOUND"
ANSWERS_LENGTH_MISMATCH = "ANSWERS_LENGTH_MISMATCH"
INVALID_QUESTION_ID = "INVALID_QUESTION_ID"
INVALID_OPTION_INDEX = "INVALID_OPTION_INDEX"
INVALID_TIME = "INVALID_TIME"
EVALUATION_FAILED = "EVALUATION_FAILED"

# Asahi chatbot (POST /chat)
CHAT_UNAVAILABLE = "CHAT_UNAVAILABLE"    # GITHUB_TOKEN not configured
CHAT_FAILED = "CHAT_FAILED"              # upstream GitHub Models call failed
CHAT_RATE_LIMITED = "CHAT_RATE_LIMITED"  # too many requests from one client
