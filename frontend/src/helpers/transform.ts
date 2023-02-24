import dayjs from 'dayjs';

const isDayJs = (v: any): boolean => {
  return dayjs.isDayjs(v);
};

const isIsoDate = (v: any): boolean => {
  const date = dayjs(v);
  return date.isValid();
};

const isNumeric = (v: any): boolean => {
  return !isNaN(parseFloat(v)) && isFinite(v);
};

const isArray = (v: any): boolean => {
  return Array.isArray(v);
};

const isBoolean = (v: any): boolean => {
  return v === 'true' || v === 'false' || typeof v == 'boolean';
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

export const transformValueFromServer = (value: any): any => {
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
