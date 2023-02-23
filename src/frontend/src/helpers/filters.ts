import * as dayjs from 'dayjs';

const transformFilterValue = (value: any): any => {
  if (Array.isArray(value)) {
    return value.map(transformFilterValue);
  }
  if (dayjs.isDayjs(value)) {
    return value.toISOString();
  }
  return value;
};

export const transformFilters = (filters: any) => {
  return Object.fromEntries(Object.entries(filters).map(([k, v]) => [k, transformFilterValue(v)]));
};
