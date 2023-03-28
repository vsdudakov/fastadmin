import { Checkbox, Tag } from 'antd';
import dayjs from 'dayjs';
import slugify from 'slugify';

export const isDayJs = (v: any): boolean => {
  return dayjs.isDayjs(v);
};

export const isIsoDate = (v: any): boolean => {
  const date = dayjs(v);
  return date.isValid();
};

export const isNumeric = (v: any): boolean => {
  return !isNaN(parseFloat(v)) && isFinite(v);
};

export const isArray = (v: any): boolean => {
  return Array.isArray(v);
};

export const isBoolean = (v: any): boolean => {
  return v === 'true' || v === 'false' || typeof v === 'boolean' || !!v === v;
};

export const isString = (v: any): boolean => {
  return typeof v === 'string' || v instanceof String;
};

export const isJson = (v: any): boolean => {
  if (!isString(v)) {
    try {
      v = JSON.stringify(v);
    } catch (e) {
      return false;
    }
  }
  try {
    JSON.parse(v);
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
  if (isArray(value)) {
    return value.map(transformValueToServer);
  }
  if (isDayJs(value)) {
    return value.toISOString();
  }
  return value;
};

export const transformDataToServer = (data: any) => {
  return Object.fromEntries(Object.entries(data).map(([k, v]) => [k, transformValueToServer(v)]));
};

export const transformFiltersToServer = (data: any) => {
  const filters = transformDataToServer(data);
  const filtersData: Record<string, string> = {};
  Object.entries(filters).forEach(([k, v]) => {
    if (isArray(v) && v.length === 2 && v.every(isIsoDate)) {
      filtersData[`${k}__gte`] = v[0];
      filtersData[`${k}__lte`] = v[1];
      return;
    }
    if (isArray(v)) {
      filtersData[`${k}__in`] = v;
      return;
    }
    if (isIsoDate(v) || isNumeric(v) || isBoolean(v)) {
      filtersData[k] = v;
      return;
    }
    filtersData[`${k}__icontains`] = v;
  });
  return filtersData;
};

export const transformValueFromServer = (value: any): any => {
  if (value === null || value === undefined) {
    return value;
  }
  if (isArray(value)) {
    return value.map(transformValueFromServer);
  }
  if (isNumeric(value)) {
    return value;
  }
  if (isBoolean(value)) {
    return value !== 'false' && !!value;
  }
  if (isIsoDate(value)) {
    return dayjs(value);
  }
  return value;
};

export const transformDataFromServer = (data: any) => {
  return Object.fromEntries(Object.entries(data).map(([k, v]) => [k, transformValueFromServer(v)]));
};

export const transformColumnValueFromServer = (
  value: any,
  emptyValue?: string,
  dateTimeFormat?: string
) => {
  if (isBoolean(value)) {
    return <Checkbox checked={value} />;
  }
  if (isNumeric(value)) {
    return value;
  }
  if (isIsoDate(value) && dateTimeFormat) {
    return dayjs(value).format(dateTimeFormat);
  }
  if (isArray(value)) {
    const colors = [
      'blue',
      'purple',
      'cyan',
      'green',
      'magenta',
      'pink',
      'red',
      'orange',
      'yellow',
      'volcano',
      'geekblue',
      'lime',
      'gold',
    ];

    return value.map((v: any, index: number) => {
      return (
        <Tag color={colors[index % colors.length]} key={v}>
          {v}
        </Tag>
      );
    });
  }
  return value || emptyValue || '-';
};
