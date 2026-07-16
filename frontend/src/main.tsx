import { QueryClient } from "@tanstack/react-query";
import i18next from "i18next";
import React from "react";
import ReactDOM from "react-dom/client";
import { initReactI18next } from "react-i18next";

import { App } from "@/containers/app/index.tsx";
import { getLanguage, resources } from "@/locales";
import { ExternalProviders, InternalProviders } from "@/providers.tsx";

import "./index.css";

const queryClient = new QueryClient();

i18next.use(initReactI18next).init({
  resources,
  lng: getLanguage(),
  fallbackLng: "en",
  defaultNS: "translation",
  // Components request per-component namespaces; all keys live in "translation"
  fallbackNS: "translation",
  // Keys are natural-language sentences: "." and ":" are not separators
  keySeparator: false,
  nsSeparator: false,
  interpolation: { escapeValue: false }, // React already does escaping
});

const root = document.getElementById("root");
if (!root) throw new Error("Root element not found");

ReactDOM.createRoot(root).render(
  <React.StrictMode>
    <ExternalProviders client={queryClient} i18n={i18next}>
      <InternalProviders>
        <App />
      </InternalProviders>
    </ExternalProviders>
  </React.StrictMode>,
);
