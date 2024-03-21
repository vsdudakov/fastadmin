import type { IModel } from "@/interfaces/configuration";

export const getTitleFromFieldName = (value: string) => {
  const str = value.replace("_", " ");
  return str.charAt(0).toUpperCase() + str.slice(1);
};

export const getTitleFromModel = (model: IModel, plural = false) => {
  if (plural && model.verbose_name_plural) {
    return model.verbose_name_plural;
  }
  if (model.verbose_name) {
    return plural ? `${model.verbose_name}s` : model.verbose_name;
  }
  const name = (model.name.match(/[A-Z][a-z]+|[0-9]+/g) || [model.name]).join(
    " ",
  );
  return plural ? `${name}s` : name;
};
