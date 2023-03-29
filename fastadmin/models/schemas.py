from collections.abc import Sequence
from enum import Enum

from pydantic import BaseModel


class WidgetType(str, Enum):
    """Widget type"""

    Input = "Input"
    InputNumber = "InputNumber"
    SlugInput = "SlugInput"
    EmailInput = "EmailInput"
    PhoneInput = "PhoneInput"
    UrlInput = "UrlInput"
    PasswordInput = "PasswordInput"
    TextArea = "TextArea"
    RichTextArea = "RichTextArea"
    JsonTextArea = "JsonTextArea"
    Select = "Select"
    AsyncSelect = "AsyncSelect"
    AsyncTransfer = "AsyncTransfer"
    Switch = "Switch"
    Checkbox = "Checkbox"
    TimePicker = "TimePicker"
    DatePicker = "DatePicker"
    DateTimePicker = "DateTimePicker"
    RangePicker = "RangePicker"
    RadioGroup = "RadioGroup"
    CheckboxGroup = "CheckboxGroup"
    Upload = "Upload"


class DashboardWidgetType(str, Enum):
    """Dashboard Widget type"""

    ChartLine = "ChartLine"
    ChartArea = "ChartArea"
    ChartColumn = "ChartColumn"
    ChartBar = "ChartBar"
    ChartPie = "ChartPie"


class ModelPermission(str, Enum):
    """Model permission"""

    Add = "Add"
    Change = "Change"
    Delete = "Delete"
    Export = "Export"


class ModelAction(BaseModel):
    """Action"""

    name: str
    description: str | None


class ListConfigurationFieldSchema(BaseModel):
    """List configuration field schema"""

    index: int | None

    sorter: bool | None
    width: str | None
    is_link: bool | None
    empty_value_display: str
    filter_widget_type: WidgetType | None
    filter_widget_props: dict | None


class AddConfigurationFieldSchema(BaseModel):
    """Add configuration field schema"""

    index: int | None

    form_widget_type: WidgetType
    form_widget_props: dict | None
    required: bool | None


class ChangeConfigurationFieldSchema(BaseModel):
    """Change configuration field schema"""

    index: int | None

    form_widget_type: WidgetType
    form_widget_props: dict | None
    required: bool | None


class ModelFieldSchema(BaseModel):
    """Model field schema"""

    name: str
    list_configuration: ListConfigurationFieldSchema | None
    add_configuration: AddConfigurationFieldSchema | None
    change_configuration: ChangeConfigurationFieldSchema | None


class BaseModelSchema(BaseModel):
    """Base Model schema"""

    name: str
    permissions: Sequence[ModelPermission]
    actions: Sequence[ModelAction]
    actions_on_top: bool | None
    actions_on_bottom: bool | None
    actions_selection_counter: bool | None
    fields: Sequence[ModelFieldSchema]
    list_per_page: int | None
    search_help_text: str | None
    search_fields: Sequence[str] | None
    preserve_filters: bool | None
    list_max_show_all: int | None
    show_full_result_count: bool | None


class InlineModelSchema(BaseModelSchema):
    """Inline model schema"""

    fk_name: str
    max_num: int | None
    min_num: int | None
    verbose_name: str | None
    verbose_name_plural: str | None


class ModelSchema(BaseModelSchema):
    """Model schema"""

    fieldsets: Sequence[tuple[str | None, dict[str, Sequence[str]]]] | None
    save_on_top: bool | None
    save_as: bool | None
    save_as_continue: bool | None
    view_on_site: str | None
    inlines: Sequence[InlineModelSchema] | None


class DashboardWidgetSchema(BaseModel):
    """Dashboard widget schema"""

    key: str
    title: str
    dashboard_widget_type: DashboardWidgetType
    x_field: str
    y_field: str | None = None
    series_field: str | None = None
    x_field_filter_widget_type: WidgetType | None = None
    x_field_filter_widget_props: dict | None = None
    x_field_periods: list[str] | None = None


class ConfigurationSchema(BaseModel):
    """Configuration schema"""

    site_name: str
    site_sign_in_logo: str
    site_header_logo: str
    site_favicon: str
    primary_color: str
    username_field: str
    date_format: str
    datetime_format: str
    models: Sequence[ModelSchema]
    dashboard_widgets: Sequence[DashboardWidgetSchema]


class ModelFieldWidgetSchema(BaseModel):
    """Orm model field schema"""

    name: str
    column_name: str
    is_m2m: bool
    is_pk: bool
    is_immutable: bool
    form_widget_type: WidgetType
    form_widget_props: dict
    filter_widget_type: WidgetType
    filter_widget_props: dict
