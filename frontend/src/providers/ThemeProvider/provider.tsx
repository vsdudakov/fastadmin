import { theme } from "antd";
import type React from "react";
import { useEffect, useMemo, useState } from "react";

import { ThemeContext, type ThemeMode, type ThemePreference } from ".";

interface IThemeProviderProps {
  children?: React.ReactNode;
}

const THEME_STORAGE_KEY = "fastadmin-theme-mode";

const canUseStorage = (): boolean => {
  const storage = typeof window !== "undefined" ? window.localStorage : null;
  return (
    !!storage &&
    typeof storage === "object" &&
    typeof storage.getItem === "function" &&
    typeof storage.setItem === "function"
  );
};

const getSystemMode = (): ThemeMode =>
  typeof window !== "undefined" &&
  window.matchMedia?.("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";

const getInitialPreference = (): ThemePreference => {
  if (typeof window === "undefined") {
    return "system";
  }
  const stored = canUseStorage()
    ? (window.localStorage.getItem(THEME_STORAGE_KEY) as ThemePreference | null)
    : null;
  if (stored === "light" || stored === "dark" || stored === "system") {
    return stored;
  }
  return "system";
};

export const ThemeProvider: React.FC<IThemeProviderProps> = ({ children }) => {
  const [preference, setPreference] = useState<ThemePreference>(
    getInitialPreference,
  );
  const [systemMode, setSystemMode] = useState<ThemeMode>(getSystemMode);

  const mode: ThemeMode = preference === "system" ? systemMode : preference;

  // Follow the OS appearance while the preference is "system"
  useEffect(() => {
    const media = window.matchMedia?.("(prefers-color-scheme: dark)");
    if (!media?.addEventListener) {
      return;
    }
    const onChange = (event: MediaQueryListEvent) =>
      setSystemMode(event.matches ? "dark" : "light");
    media.addEventListener("change", onChange);
    return () => media.removeEventListener("change", onChange);
  }, []);

  useEffect(() => {
    if (canUseStorage()) {
      window.localStorage.setItem(THEME_STORAGE_KEY, preference);
    }
  }, [preference]);

  useEffect(() => {
    document.body.setAttribute("data-theme", mode);
  }, [mode]);

  const contextValue = useMemo(
    () => ({
      mode,
      preference,
      setPreference,
    }),
    [mode, preference],
  );

  // Sync Ant Design algorithm token for downstream use if needed
  const {
    token: { colorBgBase },
  } = theme.useToken();

  useEffect(() => {
    document.body.style.backgroundColor = colorBgBase;
  }, [colorBgBase]);

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  );
};
