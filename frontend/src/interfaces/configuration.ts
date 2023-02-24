export enum EFieldWidgetType {
  Input = 'Input',
  InputNumber = 'InputNumber',
  TextArea = 'TextArea',
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
  is_link?: boolean;
  empty_value_display: string;
  filter_widget_type?: EFieldWidgetType;
  filter_widget_props?: any;
  filter_condition?: string;
}

export interface IAddConfigurationField {
  form_widget_type?: EFieldWidgetType;
  form_widget_props?: any;
  required?: boolean;
}

export interface IChangeConfigurationField {
  form_widget_type?: EFieldWidgetType;
  form_widget_props?: any;
  required?: boolean;
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
  list_per_page?: number;
  save_on_top?: boolean;
  search_help_text?: string;
}

export interface IConfiguration {
  site_name: string;
  site_sign_in_logo?: string;
  site_header_logo?: string;
  site_favicon?: string;
  username_field: string;
  models: IModel[];
  primary_color?: string;
}
