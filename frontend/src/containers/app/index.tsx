import { ConfigProvider } from "antd";
import type React from "react";
import { useContext } from "react";
import { useTranslation } from "react-i18next";
import { Route, Routes } from "react-router-dom";

import { ROUTES } from "@/constants/routes";
import { Add } from "@/containers/add";
import { Change } from "@/containers/change";
import { Index } from "@/containers/index";
import { List } from "@/containers/list";
import { SignIn } from "@/containers/sign-in";
import { usePageMeta } from "@/hooks/usePageMeta";
import { ConfigurationContext } from "@/providers/ConfigurationProvider";
import { ThemeContext } from "@/providers/ThemeProvider";

export const App: React.FC = () => {
  const { configuration } = useContext(ConfigurationContext);
  const { mode } = useContext(ThemeContext);
  const { t: _t } = useTranslation("App");
  const isDark = mode === "dark";

  usePageMeta({
    faviconHref: `${window.SERVER_DOMAIN ?? ""}${configuration.site_favicon ?? ""}`,
  });

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: configuration.primary_color,
          colorLink: configuration.primary_color,
          colorLinkActive: configuration.primary_color,
          colorLinkHover: configuration.primary_color,
          borderRadius: 10,
          borderRadiusLG: 14,
          borderRadiusSM: 8,
          controlHeight: 38,
          colorBgLayout: isDark ? "#161617" : "#f5f5f7",
          colorBorder: isDark
            ? "rgba(255, 255, 255, 0.16)"
            : "rgba(0, 0, 0, 0.12)",
          colorBorderSecondary: isDark
            ? "rgba(255, 255, 255, 0.08)"
            : "rgba(0, 0, 0, 0.06)",
          colorSplit: isDark
            ? "rgba(255, 255, 255, 0.08)"
            : "rgba(0, 0, 0, 0.06)",
          fontFamily:
            '-apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
          boxShadow:
            "0 1px 2px rgba(0, 0, 0, 0.04), 0 8px 24px rgba(0, 0, 0, 0.06)",
          boxShadowSecondary:
            "0 1px 2px rgba(0, 0, 0, 0.04), 0 12px 32px rgba(0, 0, 0, 0.08)",
        },
        components: {
          Card: {
            borderRadiusLG: 16,
          },
          Button: {
            controlHeight: 38,
            fontWeight: 500,
            primaryShadow: "none",
            defaultShadow: "none",
            dangerShadow: "none",
          },
          Input: {
            controlHeight: 38,
          },
          Select: {
            controlHeight: 38,
          },
          Menu: {
            itemBorderRadius: 8,
            subMenuItemBorderRadius: 8,
            itemMarginInline: 8,
          },
          Table: {
            headerBg: "transparent",
            headerSplitColor: "transparent",
            headerColor: isDark
              ? "rgba(255, 255, 255, 0.55)"
              : "rgba(0, 0, 0, 0.55)",
          },
          Modal: {
            borderRadiusLG: 16,
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
