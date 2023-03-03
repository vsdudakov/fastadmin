/* eslint-disable no-template-curly-in-string */
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { HelmetProvider } from 'react-helmet-async';
import { HashRouter } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import i18next from 'i18next';

import { ConfigurationProvider } from 'providers/ConfigurationProvider';
import { SignInUserProvider } from 'providers/SignInUserProvider';
import { ConfigProvider } from 'antd';

interface IInternalProviders {
  children?: React.ReactNode;
}

export const InternalProviders: React.FC<IInternalProviders> = ({ children }) => (
  <SignInUserProvider>
    <ConfigurationProvider>
      {children}
    </ConfigurationProvider>
  </SignInUserProvider>
);


interface IExternalProviders {
  children?: React.ReactNode;
  client: QueryClient;
  locale?: any;
  i18n?: any;
}


export const ExternalProviders: React.FC<IExternalProviders> = ({ children, client, i18n }) => (
  <HashRouter>
    <QueryClientProvider client={client}>
      <I18nextProvider i18n={i18n}>
        <HelmetProvider>
          {children}
        </HelmetProvider>
      </I18nextProvider>
    </QueryClientProvider>
  </HashRouter>
);


export const TestProviders: React.FC<IExternalProviders> = ({ children, client }) => (
  <ExternalProviders client={client} i18n={i18next}>
    <ConfigProvider>
      {children}
    </ConfigProvider>
  </ExternalProviders>
);
