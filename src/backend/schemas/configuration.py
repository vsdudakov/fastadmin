from enum import Enum

from pydantic import BaseModel


class WidgetType(str, Enum):
    Input = "Input"
    InputNumber = "InputNumber"
    Select = "Select"
    AsyncSelect = "AsyncSelect"
    Checkbox = "Checkbox"
    TimePicker = "TimePicker"
    DatePicker = "DatePicker"
    RangePicker = "RangePicker"
    RadioGroup = "RadioGroup"
    CheckboxGroup = "CheckboxGroup"
    Upload = "Upload"


class ModelPermission(str, Enum):
    Add = "Add"
    Change = "Change"
    Delete = "Delete"
    Export = "Export"


class ListConfigurationFieldSchema(BaseModel):
    sorter: bool
    width: int | None
    widget_type: WidgetType
    widget_props: dict | None


class AddConfigurationFieldSchema(BaseModel):
    widget_type: WidgetType
    widget_props: dict | None


class ChangeConfigurationFieldSchema(BaseModel):
    widget_type: WidgetType
    widget_props: dict | None


class ModelFieldSchema(BaseModel):
    name: str
    list_configuration: ListConfigurationFieldSchema | None
    add_configuration: AddConfigurationFieldSchema | None
    change_configuration: ChangeConfigurationFieldSchema | None


class ModelSchema(BaseModel):
    name: str
    permissions: list[ModelPermission]
    fields: list[ModelFieldSchema]


class ConfigurationSchema(BaseModel):
    site_name: str
    site_sign_in_logo: str
    site_header_logo: str
    site_favicon: str
    primary_color: str
    models: list[ModelSchema]
