import type { IConfiguration, IModel } from "@/interfaces/configuration";

export const getConfigurationModel = (
  configuration: IConfiguration,
  modelName: string,
): IModel | undefined => {
  const model = configuration.models.find((item) => item.name === modelName);
  if (model) {
    return model;
  }

  for (const item of configuration.models) {
    for (const inline of item.inlines || []) {
      if (inline.name === modelName) {
        return inline as IModel;
      }
    }
  }
};
