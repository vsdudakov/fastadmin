import { describe, expect, it } from "vitest";

import { applyDayjsLocale, getAntdLocale, getLanguage, resources } from ".";

describe("locales", () => {
  it("returns the configured language when supported", () => {
    expect(getLanguage("ru")).toBe("ru");
    expect(getLanguage("de")).toBe("de");
  });

  it("normalizes region codes", () => {
    expect(getLanguage("zh-CN")).toBe("zh");
    expect(getLanguage("fr_FR")).toBe("fr");
  });

  it("falls back to the browser language when not configured", () => {
    // jsdom reports en-US
    expect(getLanguage(null)).toBe("en");
    expect(getLanguage(undefined)).toBe("en");
    expect(getLanguage("")).toBe("en");
  });

  it("skips unsupported languages", () => {
    expect(getLanguage("xx")).toBe("en");
  });

  it("has an antd locale and dayjs locale for every language", () => {
    for (const language of Object.keys(resources) as Array<
      keyof typeof resources
    >) {
      expect(getAntdLocale(language)).toBeTruthy();
      expect(() => applyDayjsLocale(language)).not.toThrow();
    }
  });

  it("provides the same set of keys in every language", () => {
    const enKeys = Object.keys(resources.en.translation).sort();
    for (const [language, bundle] of Object.entries(resources)) {
      expect(
        Object.keys(bundle.translation).sort(),
        `keys mismatch for ${language}`,
      ).toEqual(enKeys);
    }
  });
});
