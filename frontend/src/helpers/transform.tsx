import { Checkbox, Tag } from "antd";
import dayjs from "dayjs";
import slugify from "slugify";

export const isTime = (v: string): boolean => {
  // Accept common backend time shapes, including:
  // HH:mm:ss(.ffffff), HH:mm(:ss)
  // with optional timezone suffix.
  const timeLikeRegex =
    /^\d{2}:\d{2}(?::\d{2}(?:\.\d{1,6})?)?(?:Z|[+-]\d{2}:?\d{2})?$/;
  return timeLikeRegex.test(v);
};

export const isDateTime = (v: string): boolean => {
  // Accept common backend date/datetime shapes, including:
  // YYYY-MM-DD, YYYY-MM-DDTHH:mm:ss(.ffffff), YYYY-MM-DD HH:mm(:ss)
  // with optional timezone suffix.
  const dateLikeRegex =
    /^\d{4}-\d{2}-\d{2}(?:[T\s]\d{2}:\d{2}(?::\d{2}(?:\.\d{1,6})?)?(?:Z|[+-]\d{2}:?\d{2})?)?$/;
  return dateLikeRegex.test(v);
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
  if (value.date) {
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
    if (isArray(v) && v.length === 2 && v.every(isDateTime)) {
      filtersData[`${k}__gte`] = v[0];
      filtersData[`${k}__lte`] = v[1];
    } else if (isArray(v)) {
      // Serialize __in as comma-separated so one query param works (status__in=active,inactive)
      filtersData[`${k}__in`] = v.join(",");
    } else if (isDateTime(v) || isTime(v) || isNumeric(v) || isBoolean(v)) {
      filtersData[k] = v as string;
    } else {
      filtersData[`${k}__icontains`] = String(v);
    }
  }
  return filtersData;
};

export const transformValueFromServer = (value: any): any => {
  if (value === null || value === undefined) {
    return value;
  }
  if (isArray(value)) {
    return value.map(transformValueFromServer);
  }
  if (isBoolean(value)) {
    return value !== "false" && !!value;
  }
  if (isDateTime(value)) {
    return dayjs(value);
  }
  if (isTime(value)) {
    return dayjs(`1970-01-01T${value}`);
  }
  return value;
};

export const transformDataFromServer = (data: Record<string, unknown>) => {
  return Object.fromEntries(
    Object.entries(data).map(([k, v]) => [k, transformValueFromServer(v)]),
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
  if (isDateTime(value)) {
    return dayjs(value).format(dateTimeFormat);
  }
  if (isTime(value)) {
    return value;
  }
  return value;
};
