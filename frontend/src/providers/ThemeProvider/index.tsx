import React from "react";

export type ThemeMode = "light" | "dark";

interface IThemeContext {
  mode: ThemeMode;
  setMode: (mode: ThemeMode) => void;
}

export const ThemeContext = React.createContext<IThemeContext>({
  mode: "light",

  setMode: () => {},
});
