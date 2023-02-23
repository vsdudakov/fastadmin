export const getTitleFromFieldName = (value: string) => {
  const str = value.replace('_', ' ');
  return str.charAt(0).toUpperCase() + str.slice(1);
};
