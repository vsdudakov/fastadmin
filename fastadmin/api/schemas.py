from dataclasses import dataclass
from enum import Enum


class ExportFormat(str, Enum):
    """Export format"""

    CSV = "CSV"
    JSON = "JSON"


@dataclass
class ListQuerySchema:
    """List query schema"""

    limit: int | None = 10
    offset: int | None = 0
    sort_by: str | None = None
    search: str | None = None
    filters: dict[str, str | list[str]] | None = None


@dataclass
class SignInInputSchema:
    """Sign in input schema"""

    username: str
    password: str


@dataclass
class ChangePasswordInputSchema:
    """Change password input schema"""

    password: str
    confirm_password: str


@dataclass
class ExportInputSchema:
    """Export input schema"""

    format: ExportFormat | None = ExportFormat.CSV
    limit: int | None = 1000
    offset: int | None = 0
