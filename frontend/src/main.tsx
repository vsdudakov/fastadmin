import { QueryClient } from "@tanstack/react-query";
import enUS from "antd/es/locale/en_US";
import i18next from "i18next";
import React from "react";
import ReactDOM from "react-dom/client";

import { App } from "@/containers/app/index.tsx";
import { ExternalProviders, InternalProviders } from "@/providers.tsx";

import "./index.css";

const queryClient = new QueryClient();

i18next.init({
  interpolation: { escapeValue: false }, // React already does escaping
});

const root = document.getElementById("root");
if (!root) throw new Error("Root element not found");

ReactDOM.createRoot(root).render(
  <React.StrictMode>
    <ExternalProviders client={queryClient} locale={enUS} i18n={i18next}>
      <InternalProviders>
        <App />
      </InternalProviders>
    </ExternalProviders>
  </React.StrictMode>,
);
