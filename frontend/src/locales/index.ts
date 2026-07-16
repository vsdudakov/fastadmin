import type { Locale } from "antd/es/locale";
import deDE from "antd/es/locale/de_DE";
import enUS from "antd/es/locale/en_US";
import esES from "antd/es/locale/es_ES";
import frFR from "antd/es/locale/fr_FR";
import ruRU from "antd/es/locale/ru_RU";
import zhCN from "antd/es/locale/zh_CN";
import dayjs from "dayjs";

import "dayjs/locale/de";
import "dayjs/locale/es";
import "dayjs/locale/fr";
import "dayjs/locale/ru";
import "dayjs/locale/zh-cn";

import de from "./de.json";
import en from "./en.json";
import es from "./es.json";
import fr from "./fr.json";
import ru from "./ru.json";
import zh from "./zh.json";

export const resources = {
  de: { translation: de },
  en: { translation: en },
  es: { translation: es },
  fr: { translation: fr },
  ru: { translation: ru },
  zh: { translation: zh },
} as const;

export type TLanguage = keyof typeof resources;

const antdLocales: Record<TLanguage, Locale> = {
  de: deDE,
  en: enUS,
  es: esES,
  fr: frFR,
  ru: ruRU,
  zh: zhCN,
};

const dayjsLocales: Record<TLanguage, string> = {
  de: "de",
  en: "en",
  es: "es",
  fr: "fr",
  ru: "ru",
  zh: "zh-cn",
};

/** Resolve the UI language: explicit configuration first, then browser languages, then English. */
export const getLanguage = (configured?: string | null): TLanguage => {
  const candidates = [
    configured,
    ...(typeof navigator !== "undefined"
      ? [navigator.language, ...(navigator.languages || [])]
      : []),
  ];
  for (const candidate of candidates) {
    if (!candidate) {
      continue;
    }
    const base = candidate.toLowerCase().split(/[-_]/)[0];
    if (base in resources) {
      return base as TLanguage;
    }
  }
  return "en";
};

export const getAntdLocale = (language: TLanguage): Locale =>
  antdLocales[language];

export const applyDayjsLocale = (language: TLanguage): void => {
  dayjs.locale(dayjsLocales[language]);
};
