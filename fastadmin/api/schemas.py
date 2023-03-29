from enum import Enum
from uuid import UUID

from pydantic import BaseModel, validator

from fastadmin.api.exceptions import AdminApiException


class ExportFormat(str, Enum):
    """Export format"""

    CSV = "CSV"
    JSON = "JSON"


class DashboardWidgetQuerySchema(BaseModel):
    """DashboardWidge query schema"""

    min_x_field: str | None = None
    max_x_field: str | None = None
    period_x_field: str | None = None


class DashboardWidgetDataOutputSchema(BaseModel):
    """Dashboard widget data output schema"""

    results: list[dict[str, str | int | float]]
    min_x_field: str | None = None
    max_x_field: str | None = None
    period_x_field: str | None = None


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


class ChangePasswordInputSchema(BaseModel):
    """Change password input schema"""

    password: str
    confirm_password: str

    @validator("confirm_password")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise AdminApiException(422, detail="Passwords do not match")
        return v


class ExportInputSchema(BaseModel):
    """Export input schema"""

    format: ExportFormat | None = ExportFormat.CSV
    limit: int | None = 1000
    offset: int | None = 0


class ActionInputSchema(BaseModel):
    """Action input schema"""

    ids: list[int | UUID]
