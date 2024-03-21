import { AsyncSelect } from "@/components/async-select";
import { AsyncTransfer } from "@/components/async-transfer";
import { JsonTextArea } from "@/components/json-textarea";
import { PasswordInput } from "@/components/password-input";
import { PhoneNumberInput } from "@/components/phone-number-input";
import { SlugInput } from "@/components/slug-input";
import { TextEditor } from "@/components/texteditor-field";
import { UploadInput } from "@/components/upload-input";
import { EFieldWidgetType } from "@/interfaces/configuration";
import {
  Checkbox,
  DatePicker,
  Input,
  InputNumber,
  Radio,
  Select,
  Switch,
  TimePicker,
} from "antd";

export const getWidgetCls = (
  widgetType: EFieldWidgetType,
  _t: any,
  id?: string,
) => {
  switch (widgetType) {
    case EFieldWidgetType.Input:
      return [Input, {}];
    case EFieldWidgetType.InputNumber:
      return [
        InputNumber,
        {
          style: { width: "100%" },
        },
      ];
    case EFieldWidgetType.EmailInput:
      return [Input, {}];
    case EFieldWidgetType.PhoneInput:
      return [PhoneNumberInput, {}];
    case EFieldWidgetType.SlugInput:
      return [SlugInput, {}];
    case EFieldWidgetType.UrlInput:
      return [Input, {}];
    case EFieldWidgetType.PasswordInput:
      return [PasswordInput, { parentId: id }];
    case EFieldWidgetType.TextArea:
      return [Input.TextArea, {}];
    case EFieldWidgetType.RichTextArea:
      return [TextEditor, {}];
    case EFieldWidgetType.JsonTextArea:
      return [JsonTextArea, {}];
    case EFieldWidgetType.Select:
      return [
        Select,
        {
          style: { width: "100%" },
        },
      ];
    case EFieldWidgetType.AsyncSelect:
      return [
        AsyncSelect,
        {
          style: { width: "100%" },
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
          style: { width: "100%" },
        },
      ];
    case EFieldWidgetType.TimePicker:
      return [
        TimePicker,
        {
          style: { width: "100%" },
        },
      ];
    case EFieldWidgetType.DateTimePicker:
      return [DatePicker, { style: { width: "100%" }, showTime: true }];
    case EFieldWidgetType.RangePicker:
      return [
        DatePicker.RangePicker,
        { style: { width: "100%" }, placeholder: [_t("Start"), _t("End")] },
      ];
    case EFieldWidgetType.Upload:
      return [UploadInput, { parentId: id }];
    default:
      return [Input, {}];
  }
};
