import { Checkbox, Tag } from "antd";
import dayjs from "dayjs";
import slugify from "slugify";
import {
  EFieldWidgetType,
  type IModelField,
} from "@/interfaces/configuration";

// Widgets that expect a dayjs value. A server string is only parsed into a
// dayjs when its field uses one of these; otherwise a plain text field whose
// content merely looks like a date (e.g. "2024-01-01") would be corrupted.
const DATE_WIDGET_TYPES: EFieldWidgetType[] = [
  EFieldWidgetType.DatePicker,
  EFieldWidgetType.DateTimePicker,
  EFieldWidgetType.TimePicker,
  EFieldWidgetType.RangePicker,
];

export const isTime = (v: string): boolean => {
  // Accept common backend time shapes, including:
  // HH:mm:ss(.ffffff), HH:mm(:ss)
  // with optional timezone suffix.
  const timeLikeRegex =
    /^\d{2}:\d{2}(?::\d{2}(?:\.\d{1,6})?)?(?:Z|[+-]\d{2}:?\d{2})?$/;
  return timeLikeRegex.test(v);
};

export const isDate = (v: string): boolean => {
  // Accept common backend date shapes, including:
  // YYYY-MM-DD
  const dateLikeRegex = /^\d{4}-\d{2}-\d{2}$/;
  return dateLikeRegex.test(v);
};

export const isDateTime = (v: string): boolean => {
  // Accept common backend date/datetime shapes, including:
  // YYYY-MM-DDTHH:mm:ss(.ffffff), YYYY-MM-DD HH:mm(:ss)
  // with optional timezone suffix.
  const dateTimeLikeRegex =
    /^\d{4}-\d{2}-\d{2}(?:[T\s]\d{2}:\d{2}(?::\d{2}(?:\.\d{1,6})?)?(?:Z|[+-]\d{2}:?\d{2})?)?$/;
  return dateTimeLikeRegex.test(v);
};

export const isNumeric = (v: string): boolean => {
  const numericRegex = /^[+-]?(\d+(\.\d*)?|\.\d+)$/;
  return numericRegex.test(v);
};

export const isArray = (v: unknown): boolean => {
  return Array.isArray(v);
};

export const isBoolean = (v: string): boolean => {
  const booleanRegex = /^(true|false)$/i;
  return booleanRegex.test(v);
};

export const isString = (v: unknown): boolean => {
  return typeof v === "string" || v instanceof String;
};

export const isJson = (v: any): boolean => {
  let jsonString = v;
  if (!isString(v)) {
    try {
      jsonString = JSON.stringify(v);
    } catch {
      return false;
    }
  }
  try {
    JSON.parse(jsonString);
  } catch {
    return false;
  }
  return true;
};

export const isSlug = (v: any): boolean => {
  if (!isString(v)) return false;
  try {
    return slugify(v) === v;
  } catch {
    return false;
  }
};

export const transformValueToServer = (value: any): any => {
  if (!value) {
    return value;
  }
  if (isArray(value)) {
    return value.map(transformValueToServer);
  }
  // Only real dayjs values are serialized via format(). Checking `value.date`
  // would misfire on any plain object that happens to have a `date` key and
  // throw (`value.format is not a function`), aborting the save.
  if (dayjs.isDayjs(value)) {
    return value.format();
  }
  return value;
};

export const transformDataToServer = (data: any) => {
  return Object.fromEntries(
    Object.entries(data).map(([k, v]) => [k, transformValueToServer(v)]),
  );
};

export const transformFiltersToServer = (data: any) => {
  const filters = transformDataToServer(data);
  const filtersData: Record<string, string | string[]> = {};
  for (const [k, v] of Object.entries(filters)) {
    if (
      isArray(v) &&
      v.length === 2 &&
      v.every((item: any) => isDateTime(item) || isDate(item))
    ) {
      filtersData[`${k}__gte`] = v[0];
      filtersData[`${k}__lte`] = v[1];
    } else if (isArray(v)) {
      // Serialize __in as comma-separated so one query param works (status__in=active,inactive)
      filtersData[`${k}__in`] = v.join(",");
    } else if (
      isDateTime(v) ||
      isDate(v) ||
      isTime(v) ||
      isNumeric(v) ||
      isBoolean(v)
    ) {
      filtersData[k] = v as string;
    } else {
      filtersData[`${k}__icontains`] = String(v);
    }
  }
  return filtersData;
};

export const transformValueFromServer = (
  value: any,
  widgetType?: EFieldWidgetType,
): any => {
  if (value === null || value === undefined) {
    return value;
  }
  if (isArray(value)) {
    return value.map((v: any) => transformValueFromServer(v, widgetType));
  }
  if (isBoolean(value)) {
    return value !== "false" && !!value;
  }
  // Parse date/time strings into dayjs only for date widgets. When the widget
  // type is unknown, fall back to shape detection for backward compatibility.
  const parseDates =
    widgetType === undefined || DATE_WIDGET_TYPES.includes(widgetType);
  if (parseDates) {
    if (isDate(value)) {
      return dayjs(value);
    }
    if (isTime(value)) {
      return dayjs(`1970-01-01T${value}`);
    }
    if (isDateTime(value)) {
      return dayjs(value);
    }
  }
  return value;
};

// Map each field name to the widget type used on the change form, so
// transformDataFromServer can decide, per field, whether a date-looking string
// should become a dayjs (real date widget) or stay a string (e.g. a Char field).
export const getChangeWidgetTypes = (
  modelConfiguration?: { fields?: IModelField[] },
): Record<string, EFieldWidgetType | undefined> => {
  const widgetTypes: Record<string, EFieldWidgetType | undefined> = {};
  for (const field of modelConfiguration?.fields || []) {
    widgetTypes[field.name] = field.change_configuration?.form_widget_type;
  }
  return widgetTypes;
};

export const transformDataFromServer = (
  data: Record<string, unknown>,
  widgetTypes?: Record<string, EFieldWidgetType | undefined>,
) => {
  return Object.fromEntries(
    Object.entries(data).map(([k, v]) => [
      k,
      transformValueFromServer(v, widgetTypes?.[k]),
    ]),
  );
};

export const transformColumnValueFromServer = (
  value: any,
  emptyValue?: string,
  dateTimeFormat?: string,
) => {
  if (value === null || value === undefined) {
    return emptyValue || "-";
  }
  if (isArray(value)) {
    const colors = [
      "blue",
      "purple",
      "cyan",
      "green",
      "magenta",
      "pink",
      "red",
      "orange",
      "yellow",
      "volcano",
      "geekblue",
      "lime",
      "gold",
    ];

    return value.map((v: any, index: number) => {
      return (
        <Tag color={colors[index % colors.length]} key={v}>
          {v}
        </Tag>
      );
    });
  }
  if (isBoolean(value)) {
    return <Checkbox checked={value} />;
  }
  if (isDate(value)) {
    // remove time from dateTimeFormat ss optional
    const dateFormat = dateTimeFormat?.replace(/ HH:mm(:ss)?(?:.SSS)?/, "");
    return dayjs(value).format(dateFormat);
  }
  if (isTime(value)) {
    return value;
  }
  if (isDateTime(value)) {
    return dayjs(value).format(dateTimeFormat);
  }
  return value;
};
