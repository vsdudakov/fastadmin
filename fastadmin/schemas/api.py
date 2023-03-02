from enum import Enum

from pydantic import BaseModel


class ExportFormat(str, Enum):
    """Export format"""

    CSV = "CSV"


class SignInInputSchema(BaseModel):
    """Sign in input schema"""

    username: str
    password: str


class ExportSchema(BaseModel):
    """Export schema"""

    format: ExportFormat | None
    limit: int | None
    offset: int | None
