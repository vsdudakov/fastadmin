import React from "react";

import type { TLanguage } from "@/locales";

interface ILanguageContext {
  language: TLanguage;
  setLanguage: (language: TLanguage) => void;
}

export const LanguageContext = React.createContext<ILanguageContext>({
  language: "en",

  setLanguage: () => {},
});
