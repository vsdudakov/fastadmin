import React from 'react';
import ReactDOM from 'react-dom/client';
import i18next from 'i18next';
import { QueryClient } from '@tanstack/react-query';
import enUS from 'antd/es/locale/en_US';

import { App } from 'containers/app';
import { InternalProviders, ExternalProviders } from 'providers';

import reportWebVitals from './reportWebVitals';
import './index.css';

const queryClient = new QueryClient();

i18next.init({
  interpolation: { escapeValue: false }, // React already does escaping
});

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);
root.render(
  <React.StrictMode>
    <ExternalProviders client={queryClient} locale={enUS} i18n={i18next}>
      <InternalProviders>
        <App />
      </InternalProviders>
    </ExternalProviders>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
