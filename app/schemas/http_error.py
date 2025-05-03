from pydantic import BaseModel, Field
from typing import Literal


class HTTPError(BaseModel):
    """Standardised HTTP error schema for OpenAPI documentation"""
    detail: str = Field(..., description="Human readable error message")
    status: Literal["error"] = Field("error", examples=["error"], description="Constant error indicator") 