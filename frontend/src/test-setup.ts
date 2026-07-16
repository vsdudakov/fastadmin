/**
 * Vitest setup: mock browser APIs not provided by jsdom.
 */
class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}

globalThis.ResizeObserver = ResizeObserverMock as typeof ResizeObserver;

Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
});

// Unmount rendered trees after every test so React's scheduler has no
// deferred work left when vitest tears down the jsdom environment.
import { cleanup } from "@testing-library/react";
import i18next from "i18next";
import { initReactI18next } from "react-i18next";
import { afterEach } from "vitest";

import { resources } from "@/locales";

// Mirror the production i18next setup (main.tsx) so components render
// resolved translations instead of suspending on an uninitialized instance.
i18next.use(initReactI18next).init({
  resources,
  lng: "en",
  fallbackLng: "en",
  defaultNS: "translation",
  fallbackNS: "translation",
  keySeparator: false,
  nsSeparator: false,
  interpolation: { escapeValue: false },
});

afterEach(() => {
  cleanup();
});
