import { ConfigProvider } from "antd";
import type React from "react";
import { useContext } from "react";
import { Helmet } from "react-helmet-async";
import { useTranslation } from "react-i18next";
import { Route, Routes } from "react-router-dom";

import { ROUTES } from "@/constants/routes";
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
      theme={{
        token: {
          colorPrimary: configuration.primary_color,
          colorLink: configuration.primary_color,
          colorLinkActive: configuration.primary_color,
          colorLinkHover: configuration.primary_color,
          borderRadius: 6,
          borderRadiusLG: 8,
          controlHeight: 40,
          fontFamily:
            '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
        },
        components: {
          Card: {
            borderRadiusLG: 8,
          },
          Button: {
            controlHeight: 40,
            fontWeight: 500,
          },
          Input: {
            controlHeight: 40,
          },
        },
      }}
      form={{
        validateMessages: {
          required: _t(`\${label} is required.`) as string,
          types: {
            email: _t(`\${label} is not valid.`) as string,
            number: _t(`\${label} is not valid.`) as string,
          },
          number: {
            range: _t(
              `\${label} must be between \${min} and \${max}`,
            ) as string,
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
          href={`${window.SERVER_DOMAIN ?? ""}${configuration.site_favicon ?? ""}`}
        />
      </Helmet>
      <Routes>
        <Route path={ROUTES.SIGN_IN} element={<SignIn />} />
        <Route path={ROUTES.HOME} element={<Index />} />
        <Route path={ROUTES.LIST} element={<List />} />
        <Route path={ROUTES.ADD} element={<Add />} />
        <Route path={ROUTES.CHANGE} element={<Change />} />
      </Routes>
    </ConfigProvider>
  );
};
