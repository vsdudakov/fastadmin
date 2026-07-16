import type React from "react";
import { useContext, useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";

import {
  applyDayjsLocale,
  getLanguage,
  resources,
  type TLanguage,
} from "@/locales";
import { ConfigurationContext } from "@/providers/ConfigurationProvider";

import { LanguageContext } from ".";

interface ILanguageProviderProps {
  children?: React.ReactNode;
}

const LANGUAGE_STORAGE_KEY = "fastadmin-language";

const canUseStorage = (): boolean => {
  const storage = typeof window !== "undefined" ? window.localStorage : null;
  return (
    !!storage &&
    typeof storage === "object" &&
    typeof storage.getItem === "function" &&
    typeof storage.setItem === "function"
  );
};

const getStoredLanguage = (): TLanguage | null => {
  const stored = canUseStorage()
    ? window.localStorage.getItem(LANGUAGE_STORAGE_KEY)
    : null;
  return stored && stored in resources ? (stored as TLanguage) : null;
};

export const LanguageProvider: React.FC<ILanguageProviderProps> = ({
  children,
}) => {
  const { configuration } = useContext(ConfigurationContext);
  const { i18n } = useTranslation();
  const [userLanguage, setUserLanguage] = useState<TLanguage | null>(
    getStoredLanguage,
  );

  // User choice wins, then the server setting, then the browser
  const language = userLanguage ?? getLanguage(configuration.language);

  useEffect(() => {
    i18n.changeLanguage(language);
    applyDayjsLocale(language);
  }, [i18n, language]);

  const contextValue = useMemo(
    () => ({
      language,
      setLanguage: (next: TLanguage) => {
        if (canUseStorage()) {
          window.localStorage.setItem(LANGUAGE_STORAGE_KEY, next);
        }
        setUserLanguage(next);
      },
    }),
    [language],
  );

  return (
    <LanguageContext.Provider value={contextValue}>
      {children}
    </LanguageContext.Provider>
  );
};
