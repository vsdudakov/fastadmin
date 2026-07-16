import { fireEvent, render, screen } from "@testing-library/react";
import { useContext } from "react";
import { afterEach, describe, expect, it } from "vitest";

import { defaultConfiguration } from "@/providers/ConfigurationProvider";
import { ConfigurationContext } from "@/providers/ConfigurationProvider";

import { LanguageContext } from ".";
import { LanguageProvider } from "./provider";

const STORAGE_KEY = "fastadmin-language";

const Consumer = () => {
  const { language, setLanguage } = useContext(LanguageContext);
  return (
    <div>
      <span data-testid="language">{language}</span>
      <button type="button" onClick={() => setLanguage("de")}>
        switch
      </button>
    </div>
  );
};

const renderWithConfiguration = (language?: string | null) =>
  render(
    <ConfigurationContext.Provider
      value={{ configuration: { ...defaultConfiguration, language } }}
    >
      <LanguageProvider>
        <Consumer />
      </LanguageProvider>
    </ConfigurationContext.Provider>,
  );

describe("LanguageProvider", () => {
  afterEach(() => {
    window.localStorage.removeItem(STORAGE_KEY);
  });

  it("uses the server-configured language", () => {
    renderWithConfiguration("ru");
    expect(screen.getByTestId("language").textContent).toBe("ru");
  });

  it("falls back to english for unsupported configuration", () => {
    renderWithConfiguration("xx");
    expect(screen.getByTestId("language").textContent).toBe("en");
  });

  it("persists and applies the user's choice", () => {
    renderWithConfiguration("ru");
    fireEvent.click(screen.getByRole("button", { name: "switch" }));
    expect(screen.getByTestId("language").textContent).toBe("de");
    expect(window.localStorage.getItem(STORAGE_KEY)).toBe("de");
  });

  it("prefers the stored user choice over the server setting", () => {
    window.localStorage.setItem(STORAGE_KEY, "fr");
    renderWithConfiguration("ru");
    expect(screen.getByTestId("language").textContent).toBe("fr");
  });

  it("ignores an invalid stored value", () => {
    window.localStorage.setItem(STORAGE_KEY, "yy");
    renderWithConfiguration("zh");
    expect(screen.getByTestId("language").textContent).toBe("zh");
  });
});
