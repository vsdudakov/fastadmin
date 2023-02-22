from enum import Enum

from pydantic import BaseModel


class WidgetType(str, Enum):
    Input = "Input"
    InputNumber = "InputNumber"
    Select = "Select"
    MultipleSelect = "MultipleSelect"
    Checkbox = "Checkbox"
    TimePicker = "TimePicker"
    DatePicker = "DatePicker"
    RadioGroup = "RadioGroup"
    CheckboxGroup = "CheckboxGroup"
    Upload = "Upload"


class ModelFieldSchema(BaseModel):
    name: str
    widget_type: WidgetType


class ModelSchema(BaseModel):
    name: str
    fields: list[ModelFieldSchema]


class ConfigurationSchema(BaseModel):
    site_name: str
    site_sign_in_logo: str
    site_header_logo: str
    site_favicon: str
    primary_color: str
    models: list[ModelSchema]
