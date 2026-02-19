import React from "react";
import type { IConfiguration } from "@/interfaces/configuration";

export const defaultConfiguration = {
  site_name: "API Administration",
  username_field: "username",
  models: [],
  dashboard_widgets: [],
};

interface IConfigurationContext {
  configuration: IConfiguration;
}

export const ConfigurationContext = React.createContext<IConfigurationContext>({
  configuration: defaultConfiguration,
});
