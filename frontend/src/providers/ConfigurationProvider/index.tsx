import { useQuery } from "@tanstack/react-query";
import { Button, Popover, Result } from "antd";
import React from "react";
import { useTranslation } from "react-i18next";

import { getFetcher } from "@/fetchers/fetchers";
import type { IConfiguration } from "@/interfaces/configuration";

interface IConfigurationContext {
  configuration: IConfiguration;
}

interface IConfigurationProvider {
  children?: React.ReactNode;
}

const defaultConfiguration = {
  site_name: "API Administration",
  username_field: "username",
  models: [],
  dashboard_widgets: [],
};

export const ConfigurationContext = React.createContext<IConfigurationContext>({
  configuration: defaultConfiguration,
});
export const ConfigurationConsumer = ConfigurationContext.Consumer;

export const ConfigurationProvider = ({ children }: IConfigurationProvider) => {
  const { t: _t } = useTranslation("ConfigurationProvider");
  const configurationData = useQuery({
    queryKey: ["/configuration"],
    queryFn: () => getFetcher("/configuration"),
    retry: false,
    refetchOnWindowFocus: false,
  });
  if (configurationData.isLoading) {
    return null;
  }
  if (configurationData.error) {
    const error: any = configurationData.error;
    return (
      <Result
        status="warning"
        title="Invalid configuration. Please check your admin model classes and logs."
        extra={
          <Popover
            title={_t("Error")}
            content={error?.response?.data?.exception || error?.message}
            placement="bottom"
            trigger="click"
          >
            <Button type="primary" key="console">
              {_t("Show Error")}
            </Button>
          </Popover>
        }
      />
    );
  }
  return (
    <ConfigurationContext.Provider
      value={{
        configuration: (configurationData?.data ||
          defaultConfiguration) as IConfiguration,
      }}
    >
      {children}
    </ConfigurationContext.Provider>
  );
};
