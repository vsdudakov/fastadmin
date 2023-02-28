from enum import Enum

from pydantic import BaseModel


class ExportFormat(str, Enum):
    CSV = "CSV"


class SignInInputSchema(BaseModel):
    username: str
    password: str


class ExportSchema(BaseModel):
    format: ExportFormat | None
    limit: int | None
    offset: int | None
