export const getTitleFromFieldName = (value: string) => {
  const str = value.replace('_', ' ');
  return str.charAt(0).toUpperCase() + str.slice(1);
};

export const getTitleFromModelClass = (modelClass?: string) => {
  if (!modelClass) return '';
  return (modelClass.match(/[A-Z][a-z]+|[0-9]+/g) || [modelClass]).join(' ');
};
