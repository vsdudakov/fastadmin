import React from "react";

export type ThemeMode = "light" | "dark";
export type ThemePreference = ThemeMode | "system";

interface IThemeContext {
  // Resolved mode actually applied to the UI
  mode: ThemeMode;
  // User preference; "system" follows the OS setting
  preference: ThemePreference;
  setPreference: (preference: ThemePreference) => void;
}

export const ThemeContext = React.createContext<IThemeContext>({
  mode: "light",
  preference: "system",

  setPreference: () => {},
});
