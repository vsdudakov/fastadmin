import { theme } from "antd";
import type React from "react";
import { useEffect, useMemo, useState } from "react";

import { ThemeContext, type ThemeMode } from ".";

interface IThemeProviderProps {
  children?: React.ReactNode;
}

const THEME_STORAGE_KEY = "fastadmin-theme-mode";

const getInitialMode = (): ThemeMode => {
  if (typeof window === "undefined") {
    return "light";
  }

  const storage = window.localStorage;
  const canReadStorage =
    storage &&
    typeof storage === "object" &&
    typeof storage.getItem === "function";
  const stored = canReadStorage
    ? (storage.getItem(THEME_STORAGE_KEY) as ThemeMode | null)
    : null;
  if (stored === "light" || stored === "dark") {
    return stored;
  }

  if (window.matchMedia?.("(prefers-color-scheme: dark)").matches) {
    return "dark";
  }

  return "light";
};

export const ThemeProvider: React.FC<IThemeProviderProps> = ({ children }) => {
  const [mode, setMode] = useState<ThemeMode>(getInitialMode);

  useEffect(() => {
    const storage = window.localStorage;
    if (
      storage &&
      typeof storage === "object" &&
      typeof storage.setItem === "function"
    ) {
      storage.setItem(THEME_STORAGE_KEY, mode);
    }
    document.body.setAttribute("data-theme", mode);
  }, [mode]);

  const contextValue = useMemo(
    () => ({
      mode,
      setMode,
    }),
    [mode],
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
