import { type QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ConfigProvider } from "antd";
import i18next from "i18next";
import { HelmetProvider } from "react-helmet-async";
import { I18nextProvider } from "react-i18next";
import { HashRouter } from "react-router-dom";

import { ConfigurationProvider } from "@/providers/ConfigurationProvider/provider";
import { SignInUserProvider } from "@/providers/SignInUserProvider/provider";

interface IInternalProviders {
  children?: React.ReactNode;
}

export const InternalProviders: React.FC<IInternalProviders> = ({
  children,
}) => (
  <SignInUserProvider>
    <ConfigurationProvider>{children}</ConfigurationProvider>
  </SignInUserProvider>
);

interface IExternalProviders {
  children?: React.ReactNode;
  client: QueryClient;

  locale?: any;

  i18n?: any;
}

export const ExternalProviders: React.FC<IExternalProviders> = ({
  children,
  client,
  i18n,
}) => (
  <HashRouter>
    <QueryClientProvider client={client}>
      <I18nextProvider i18n={i18n}>
        <HelmetProvider>{children}</HelmetProvider>
      </I18nextProvider>
    </QueryClientProvider>
  </HashRouter>
);

export const TestProviders: React.FC<IExternalProviders> = ({
  children,
  client,
}) => (
  <ExternalProviders client={client} i18n={i18next}>
    <ConfigProvider>{children}</ConfigProvider>
  </ExternalProviders>
);
