import { Checkbox, DatePicker, Input, InputNumber, Radio, Select, TimePicker, Upload } from 'antd';
import { EFieldWidgetType } from 'interfaces/configuration';

export const getWidgetCls = (widgetType: EFieldWidgetType, _t: any) => {
  switch (widgetType) {
    case EFieldWidgetType.Input:
      return [Input, {}];
    case EFieldWidgetType.InputNumber:
      return [InputNumber, {}];
    case EFieldWidgetType.Select:
      return [Select, {}];
    case EFieldWidgetType.AsyncSelect:
      return [Select, {}];
    case EFieldWidgetType.Checkbox:
      return [Checkbox, {}];
    case EFieldWidgetType.CheckboxGroup:
      return [Checkbox.Group, {}];
    case EFieldWidgetType.RadioGroup:
      return [Radio.Group, {}];
    case EFieldWidgetType.DatePicker:
      return [DatePicker, { style: { width: '100%' } }];
    case EFieldWidgetType.TimePicker:
      return [TimePicker, { style: { width: '100%' } }];
    case EFieldWidgetType.RangePicker:
      return [
        DatePicker.RangePicker,
        { style: { width: '100%' }, placeholder: [_t('Start'), _t('End')] },
      ];
    case EFieldWidgetType.Upload:
      return [Upload, {}];
    default:
      return [Input, {}];
  }
};
