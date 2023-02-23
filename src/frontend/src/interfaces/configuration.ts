export enum EFieldWidgetType {
  Input = 'Input',
  InputNumber = 'InputNumber',
  Select = 'Select',
  AsyncSelect = 'AsyncSelect',
  Switch = 'Switch',
  Checkbox = 'Checkbox',
  TimePicker = 'TimePicker',
  DatePicker = 'DatePicker',
  DateTimePicker = 'DateTimePicker',
  RangePicker = 'RangePicker',
  RadioGroup = 'RadioGroup',
  CheckboxGroup = 'CheckboxGroup',
  Upload = 'Upload',
}

export enum EModelPermission {
  Add = 'Add',
  Change = 'Change',
  Delete = 'Delete',
  Export = 'Export',
}

export interface IListConfigurationField {
  sorter?: boolean;
  width?: number;
  widget_type?: EFieldWidgetType;
  widget_props?: any;
  filter_condition?: string;
  col?: number;
}

export interface IAddConfigurationField {
  widget_type?: EFieldWidgetType;
  widget_props?: any;
  required?: boolean;
  row?: number;
  col?: number;
}

export interface IChangeConfigurationField {
  widget_type?: EFieldWidgetType;
  widget_props?: any;
  required?: boolean;
  row?: number;
  col?: number;
}

export interface IModelField {
  name: string;
  list_configuration?: IListConfigurationField;
  add_configuration?: IAddConfigurationField;
  change_configuration?: IChangeConfigurationField;
}

export interface IModel {
  name: string;
  permissions: EModelPermission[];
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
