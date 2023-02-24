import React from 'react';
import { useQuery } from '@tanstack/react-query';

import { getFetcher } from 'fetchers/fetchers';

import { IConfiguration } from 'interfaces/configuration';

interface IConfigurationContext {
  configuration: IConfiguration;
}

interface IConfigurationProvider {
  children?: React.ReactNode;
}

const defaultConfiguration = {
  site_name: 'API Administration',
  models: [],
};

export const ConfigurationContext = React.createContext<IConfigurationContext>({
  configuration: defaultConfiguration,
});
export const ConfigurationConsumer = ConfigurationContext.Consumer;

export const ConfigurationProvider = ({ children }: IConfigurationProvider) => {
  const configurationData = useQuery(['/configuration'], () => getFetcher('/configuration'), {
    retry: false,
    refetchOnWindowFocus: false,
  });
  if (configurationData.isLoading) {
    return null;
  }
  return (
    <ConfigurationContext.Provider
      value={{
        configuration: (configurationData?.data || defaultConfiguration) as IConfiguration,
      }}
    >
      {children}
    </ConfigurationContext.Provider>
  );
};
