import typing as tp
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from uuid import UUID


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
    UploadFile = "UploadFile"
    UploadImage = "UploadImage"


class WidgetActionType(str, Enum):
    """Widget action type"""

    ChartLine = "ChartLine"
    ChartArea = "ChartArea"
    ChartColumn = "ChartColumn"
    ChartBar = "ChartBar"
    ChartPie = "ChartPie"
    Action = "Action"


class ModelPermission(str, Enum):
    """Model permission"""

    Add = "Add"
    Change = "Change"
    Delete = "Delete"
    Export = "Export"


class ActionResponseType(str, Enum):
    """Action response type"""

    DOWNLOAD_BASE64 = "DOWNLOAD_BASE64"
    MESSAGE = "MESSAGE"


@dataclass
class WidgetActionChartProps:
    """Widget action chart props"""

    x_field: str
    y_field: str
    series_field: str | None = None
    series_color: list[str] | dict[str, str] | None = None


@dataclass
class WidgetActionParentArgumentProps:
    """Widget action parent argument props"""

    name: str
    value: tp.Any


@dataclass
class WidgetActionArgumentProps:
    """Widget action chart props"""

    name: str
    widget_type: WidgetType
    widget_props: dict | None = None

    # if None, show always
    # if not None, show only if parent selected/input value is equal to the parent_argument.value
    parent_argument: WidgetActionParentArgumentProps | None = None


@dataclass
class WidgetActionProps:
    """Widget action props"""

    arguments: list[WidgetActionArgumentProps]


@dataclass
class WidgetActionFilter:
    """Model widget filter action"""

    field_name: str
    widget_type: WidgetType
    widget_props: dict | None = None


@dataclass
class ModelAction:
    """Action"""

    name: str
    description: str | None


@dataclass
class ModelWidgetAction:
    """Widget action"""

    name: str
    title: str
    description: str | None
    tab: str
    sub_tab: str | None
    width: int | None
    max_height: int | None
    widget_action_type: WidgetActionType
    widget_action_props: WidgetActionChartProps | WidgetActionProps | None = None
    widget_action_filters: list[WidgetActionFilter] | None = None


@dataclass
class ListConfigurationFieldSchema:
    """List configuration field schema"""

    index: int | None

    sorter: bool | str | None
    width: str | None
    is_link: bool | None
    empty_value_display: str
    filter_widget_type: WidgetType | None
    filter_widget_props: dict | None


@dataclass
class AddConfigurationFieldSchema:
    """Add configuration field schema"""

    index: int | None

    form_widget_type: WidgetType
    form_widget_props: dict | None
    required: bool | None


@dataclass
class ChangeConfigurationFieldSchema:
    """Change configuration field schema"""

    index: int | None

    form_widget_type: WidgetType
    form_widget_props: dict | None
    required: bool | None


@dataclass
class ModelFieldSchema:
    """Model field schema"""

    name: str
    list_configuration: ListConfigurationFieldSchema | None
    add_configuration: AddConfigurationFieldSchema | None
    change_configuration: ChangeConfigurationFieldSchema | None


@dataclass
class BaseModelSchema:
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
    verbose_name: str | None
    verbose_name_plural: str | None

    widget_actions: Sequence[ModelWidgetAction] | None


@dataclass
class InlineModelSchema(BaseModelSchema):
    """Inline model schema"""

    fk_name: str
    max_num: int | None
    min_num: int | None


@dataclass
class ModelSchema(BaseModelSchema):
    """Model schema"""

    menu_section: str | None
    fieldsets: Sequence[tuple[str | None, dict[str, Sequence[str]]]] | None
    save_on_top: bool | None
    save_as: bool | None
    save_as_continue: bool | None
    view_on_site: str | None
    inlines: Sequence[InlineModelSchema] | None


@dataclass
class ConfigurationSchema:
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


@dataclass
class ModelFieldWidgetSchema:
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


@dataclass
class ActionInputSchema:
    """Action input schema"""

    ids: list[int | str | UUID]


@dataclass
class ActionResponseSchema:
    """Action response schema"""

    type: ActionResponseType
    data: str
    file_name: str | None = None


@dataclass
class WidgetActionQuerySchema:
    """Widget action query schema"""

    field_name: str
    widget_type: WidgetType
    value: tp.Any


@dataclass
class WidgetActionInputSchema:
    """Widget action input schema"""

    query: list[WidgetActionQuerySchema]


@dataclass
class WidgetActionResponseSchema:
    """Widget action response schema"""

    data: list[dict[str, tp.Any]]
