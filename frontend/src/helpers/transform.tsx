import { Checkbox, Tag } from "antd";
import dayjs from "dayjs";
import slugify from "slugify";

export const isDayJs = (v: string): boolean => {
  const iso8601Regex =
    /^(\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2}))?)$/;
  return iso8601Regex.test(v);
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
    } catch (e) {
      return false;
    }
  }
  try {
    JSON.parse(jsonString);
  } catch (e) {
    return false;
  }
  return true;
};

export const isSlug = (v: any): boolean => {
  if (!isString(v)) return false;
  try {
    return slugify(v) === v;
  } catch (e) {
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
  const filtersData: Record<string, string> = {};
  for (const [k, v] of Object.entries(filters)) {
    if (isArray(v) && v.length === 2 && v.every(isDayJs)) {
      filtersData[`${k}__gte`] = v[0];
      filtersData[`${k}__lte`] = v[1];
      return filtersData;
    }
    if (isArray(v)) {
      filtersData[`${k}__in`] = v;
      return filtersData;
    }
    if (isDayJs(v) || isNumeric(v) || isBoolean(v)) {
      filtersData[k] = v;
      return filtersData;
    }
    filtersData[`${k}__icontains`] = v;
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
  if (isDayJs(value)) {
    return dayjs(value);
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
  if (isDayJs(value)) {
    return dayjs(value).format(dateTimeFormat);
  }
  return value;
};
