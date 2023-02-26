import {
  Checkbox,
  DatePicker,
  Input,
  InputNumber,
  Radio,
  Select,
  Switch,
  TimePicker,
  Upload,
} from 'antd';
import { AsyncSelect } from 'components/async-select';
import { AsyncTransfer } from 'components/async-transfer';
import { EFieldWidgetType } from 'interfaces/configuration';

export const getWidgetCls = (widgetType: EFieldWidgetType, _t: any) => {
  switch (widgetType) {
    case EFieldWidgetType.Input:
      return [Input, {}];
    case EFieldWidgetType.InputNumber:
      return [
        InputNumber,
        {
          style: { width: '100%' },
        },
      ];
    case EFieldWidgetType.TextArea:
      return [Input.TextArea, {}];
    case EFieldWidgetType.Select:
      return [
        Select,
        {
          style: { width: '100%' },
        },
      ];
    case EFieldWidgetType.AsyncSelect:
      return [
        AsyncSelect,
        {
          style: { width: '100%' },
        },
      ];
    case EFieldWidgetType.AsyncTransfer:
      return [AsyncTransfer, {}];
    case EFieldWidgetType.Switch:
      return [Switch, {}];
    case EFieldWidgetType.Checkbox:
      return [Checkbox, {}];
    case EFieldWidgetType.CheckboxGroup:
      return [Checkbox.Group, {}];
    case EFieldWidgetType.RadioGroup:
      return [Radio.Group, {}];
    case EFieldWidgetType.DatePicker:
      return [
        DatePicker,
        {
          style: { width: '100%' },
        },
      ];
    case EFieldWidgetType.TimePicker:
      return [
        TimePicker,
        {
          style: { width: '100%' },
        },
      ];
    case EFieldWidgetType.DateTimePicker:
      return [DatePicker, { style: { width: '100%' }, showTime: true }];
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
