/* eslint-disable no-template-curly-in-string */
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { HelmetProvider } from 'react-helmet-async';
import { HashRouter } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';

import { ConfigurationProvider } from 'providers/ConfigurationProvider';
import { SignInUserProvider } from 'providers/SignInUserProvider';

interface IProviders {
  children?: React.ReactNode;
  client: QueryClient;
  locale?: any;
  i18n?: any;
}

export const Providers = ({ children, client, i18n }: IProviders) => (
  <HashRouter>
    <QueryClientProvider client={client}>
      <I18nextProvider i18n={i18n}>
        <HelmetProvider>
          <SignInUserProvider>
            <ConfigurationProvider>{children}</ConfigurationProvider>
          </SignInUserProvider>
        </HelmetProvider>
      </I18nextProvider>
    </QueryClientProvider>
  </HashRouter>
);
