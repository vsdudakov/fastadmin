import type React from "react";
import { useContext } from "react";

import { ConfigProvider } from "antd";
import { Helmet } from "react-helmet-async";
import { useTranslation } from "react-i18next";
import { Route, Routes } from "react-router-dom";

import { Add } from "@/containers/add";
import { Change } from "@/containers/change";
import { Index } from "@/containers/index";
import { List } from "@/containers/list";
import { SignIn } from "@/containers/sign-in";
import { ConfigurationContext } from "@/providers/ConfigurationProvider";

export const App: React.FC = () => {
  const { configuration } = useContext(ConfigurationContext);
  const { t: _t } = useTranslation("App");
  return (
    <ConfigProvider
      // https://ant.design/docs/react/customize-theme#theme
      theme={{
        token: {
          colorPrimary: configuration.primary_color,
          colorLink: configuration.primary_color,
          colorLinkActive: configuration.primary_color,
          colorLinkHover: configuration.primary_color,
        },
      }}
      form={{
        validateMessages: {
          required: _t("${label} is required.") as string,
          types: {
            email: _t("${label} is not valid.") as string,
            number: _t("${label} is not valid.") as string,
          },
          number: {
            range: _t("${label} must be between ${min} and ${max}") as string,
          },
        },
      }}
    >
      <Helmet
        titleTemplate="FastAPI Admin | %s"
        defaultTitle={_t("FastAPI Admin") as string}
      >
        <meta name="description" content={_t("FastAPI Admin") as string} />
        <link
          rel="icon"
          href={(window as any).SERVER_DOMAIN + configuration.site_favicon}
        />
      </Helmet>
      <Routes>
        <Route path="/sign-in" element={<SignIn />} />
        <Route path="/" element={<Index />} />
        <Route path="/list/:model" element={<List />} />
        <Route path="/add/:model" element={<Add />} />
        <Route path="/change/:model/:id" element={<Change />} />
      </Routes>
    </ConfigProvider>
  );
};
