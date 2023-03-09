from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class ExportFormat(str, Enum):
    """Export format"""

    CSV = "CSV"


class SignInInputSchema(BaseModel):
    """Sign in input schema"""

    username: str
    password: str


class ExportInputSchema(BaseModel):
    """Export input schema"""

    format: ExportFormat | None
    limit: int | None
    offset: int | None


class ActionInputSchema(BaseModel):
    """Action input schema"""

    ids: list[int | UUID]
