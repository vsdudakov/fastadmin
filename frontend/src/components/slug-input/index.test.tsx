import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import type React from "react";
import { afterEach, describe, expect, test, vi } from "vitest";

import { SlugInput } from "./index";

vi.mock("react-i18next", async () => {
  const actual =
    await vi.importActual<typeof import("react-i18next")>("react-i18next");
  return {
    ...actual,
    useTranslation: () => ({
      t: (key: string) => key,
      i18n: { changeLanguage: vi.fn() },
    }),
  };
});

vi.mock("antd", () => ({
  Space: {
    Compact: ({ children }: { children: React.ReactNode }) => (
      <div>{children}</div>
    ),
  },
  Tooltip: ({ children }: { children: React.ReactNode }) => (
    <div>{children}</div>
  ),
  Button: ({
    children,
    onClick,
  }: {
    children: React.ReactNode;
    onClick?: () => void;
  }) => (
    <button type="button" onClick={onClick}>
      {children}
    </button>
  ),
  Input: ({
    value,
    onChange,
  }: {
    value?: string;
    onChange?: (value: unknown) => void;
  }) => <input value={value} onChange={() => onChange?.("typed")} readOnly />,
}));

describe("SlugInput", () => {
  afterEach(() => {
    cleanup();
  });

  test("slugifies value when swap clicked and onChange exists", () => {
    const onChange = vi.fn();
    render(<SlugInput value="Hello World" onChange={onChange} />);

    fireEvent.click(screen.getByRole("button"));
    expect(onChange).toHaveBeenCalledWith("Hello-World");
  });

  test("does not throw when onChange is missing", () => {
    render(<SlugInput value="No Callback" />);

    fireEvent.click(screen.getAllByRole("button")[0]);
    expect(screen.getByRole("textbox")).toBeTruthy();
  });
});
