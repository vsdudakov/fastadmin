import React, { useContext } from 'react';

import { Helmet } from 'react-helmet-async';
import { Route, Routes } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ConfigProvider } from 'antd';

import { List } from 'containers/list';
import { Add } from 'containers/add';
import { Change } from 'containers/change';
import { History } from 'containers/history';
import { SignIn } from 'containers/sign-in';
import { Index } from 'containers/index';
import { ConfigurationContext } from 'providers/ConfigurationProvider';

export const App: React.FC = () => {
  const { configuration } = useContext(ConfigurationContext);
  const { t: _t } = useTranslation('App');
  return (
    <ConfigProvider
      // https://ant.design/docs/react/customize-theme#theme
      theme={{
        token: {
          colorPrimary: configuration.primary_color,
          colorLink: configuration.primary_color,
        },
      }}
    >
      <Helmet titleTemplate="FastAPI Admin | %s" defaultTitle={_t('FastAPI Admin') as string}>
        <meta name="description" content={_t('FastAPI Admin') as string} />
        <link rel="icon" href={(window as any).SERVER_FOMAIN + configuration.site_favicon}></link>
      </Helmet>
      <Routes>
        <Route path="/sign-in" element={<SignIn />} />
        <Route path="/" element={<Index />} />
        <Route path="/list/:model" element={<List />} />
        <Route path="/add/:model" element={<Add />} />
        <Route path="/change/:model/:id" element={<Change />} />
        <Route path="/history/:model/:id" element={<History />} />
      </Routes>
    </ConfigProvider>
  );
};
