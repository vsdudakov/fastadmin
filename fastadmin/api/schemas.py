from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class ExportFormat(str, Enum):
    """Export format"""

    CSV = "CSV"
    JSON = "JSON"


class ListQuerySchema(BaseModel):
    """List query schema"""

    limit: int | None = 10
    offset: int | None = 0
    sort_by: str | None = None
    search: str | None = None
    filters: dict[str, str] | None = None


class SignInInputSchema(BaseModel):
    """Sign in input schema"""

    username: str
    password: str


class ExportInputSchema(BaseModel):
    """Export input schema"""

    format: ExportFormat | None = ExportFormat.CSV
    limit: int | None = 1000
    offset: int | None = 0


class ActionInputSchema(BaseModel):
    """Action input schema"""

    ids: list[int | UUID]
