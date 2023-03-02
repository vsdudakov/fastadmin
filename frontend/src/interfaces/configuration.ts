export enum EFieldWidgetType {
  Input = 'Input',
  InputNumber = 'InputNumber',
  TextArea = 'TextArea',
  Select = 'Select',
  AsyncSelect = 'AsyncSelect',
  AsyncTransfer = 'AsyncTransfer',
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
  index?: number;
  sorter?: boolean;
  width?: number;
  is_link?: boolean;
  empty_value_display: string;
  filter_widget_type?: EFieldWidgetType;
  filter_widget_props?: any;
}

export interface IAddConfigurationField {
  index?: number;
  form_widget_type?: EFieldWidgetType;
  form_widget_props?: any;
  required?: boolean;
}

export interface IChangeConfigurationField {
  index?: number;
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
  save_as?: boolean;
  save_as_continue?: boolean;
  view_on_site?: string;
  search_help_text?: string;
  search_fields?: string[];
  preserve_filters?: boolean;
  list_max_show_all?: number;
  show_full_result_count?: boolean;
}

export interface IConfiguration {
  site_name: string;
  site_sign_in_logo?: string;
  site_header_logo?: string;
  site_favicon?: string;
  primary_color?: string;
  username_field: string;
  date_format?: string;
  datetime_format?: string;
  models: IModel[];
}
