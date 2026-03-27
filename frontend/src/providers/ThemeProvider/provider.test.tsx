import { cleanup, render, screen } from "@testing-library/react";
import { useContext } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ThemeContext } from ".";
import { ThemeProvider } from "./provider";

const STORAGE_KEY = "fastadmin-theme-mode";

const ModeProbe = () => {
  const { mode } = useContext(ThemeContext);
  return <div data-testid="mode">{mode}</div>;
};

describe("ThemeProvider", () => {
  const originalMatchMedia = window.matchMedia;
  const originalLocalStorage = window.localStorage;

  afterEach(() => {
    cleanup();
    Object.defineProperty(window, "matchMedia", {
      configurable: true,
      writable: true,
      value: originalMatchMedia,
    });
    Object.defineProperty(window, "localStorage", {
      configurable: true,
      writable: true,
      value: originalLocalStorage,
    });
    document.body.removeAttribute("data-theme");
  });

  it("uses mode stored in localStorage", () => {
    const storageMock = {
      getItem: vi
        .fn()
        .mockImplementation((key: string) =>
          key === STORAGE_KEY ? "dark" : null,
        ),
      setItem: vi.fn(),
    };
    Object.defineProperty(window, "localStorage", {
      configurable: true,
      writable: true,
      value: storageMock,
    });

    render(
      <ThemeProvider>
        <ModeProbe />
      </ThemeProvider>,
    );

    expect(screen.getByTestId("mode").textContent).toBe("dark");
    expect(document.body.getAttribute("data-theme")).toBe("dark");
    expect(storageMock.setItem).toHaveBeenCalledWith(STORAGE_KEY, "dark");
  });

  it("falls back to dark mode from system preference", () => {
    const storageMock = {
      getItem: vi.fn().mockReturnValue("invalid"),
      setItem: vi.fn(),
    };
    Object.defineProperty(window, "localStorage", {
      configurable: true,
      writable: true,
      value: storageMock,
    });
    Object.defineProperty(window, "matchMedia", {
      configurable: true,
      writable: true,
      value: vi.fn().mockReturnValue({ matches: true }),
    });

    render(
      <ThemeProvider>
        <ModeProbe />
      </ThemeProvider>,
    );

    expect(screen.getByTestId("mode").textContent).toBe("dark");
  });

  it("handles non-standard localStorage objects", () => {
    Object.defineProperty(window, "localStorage", {
      configurable: true,
      writable: true,
      value: {},
    });

    render(
      <ThemeProvider>
        <ModeProbe />
      </ThemeProvider>,
    );

    expect(screen.getByTestId("mode").textContent).toBe("light");
    expect(document.body.getAttribute("data-theme")).toBe("light");
  });
});
