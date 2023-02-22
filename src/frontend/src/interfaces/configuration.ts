export enum EFieldWidgetType {
  Input = 'Input',
  InputNumber = 'InputNumber',
  Select = 'Select',
  MultipleSelect = 'MultipleSelect',
  Checkbox = 'Checkbox',
  TimePicker = 'TimePicker',
  DatePicker = 'DatePicker',
  RadioGroup = 'RadioGroup',
  CheckboxGroup = 'CheckboxGroup',
  Upload = 'Upload',
}

export interface IModelField {
  name: string;
  widget_type: EFieldWidgetType;
}

export interface IModel {
  name: string;
  fields: IModelField[];
}

export interface IConfiguration {
  site_name: string;
  site_sign_in_logo?: string;
  site_header_logo?: string;
  site_favicon?: string;
  models: IModel[];
  primary_color?: string;
}
