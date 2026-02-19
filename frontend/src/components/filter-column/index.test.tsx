import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { Input } from "antd";
import { afterEach, describe, expect, it, vi } from "vitest";
import { EFieldWidgetType } from "@/interfaces/configuration";
import { FilterColumn } from "./index";

const { mockGetWidgetCls } = vi.hoisted(() => ({
  mockGetWidgetCls: vi.fn(),
}));

vi.mock("@/helpers/widgets", () => ({
  getWidgetCls: (...args: unknown[]) => mockGetWidgetCls(...args),
}));

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

describe("FilterColumn", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("handles Input-based onChange and filter/reset buttons", () => {
    mockGetWidgetCls.mockReturnValue([Input, {}]);
    const onFilter = vi.fn();
    const onReset = vi.fn();

    render(
      <FilterColumn
        widgetType={EFieldWidgetType.Input}
        value="start"
        onFilter={onFilter}
        onReset={onReset}
      />,
    );

    const input = screen.getByPlaceholderText("Filter By");
    fireEvent.change(input, { target: { value: "john" } });

    fireEvent.click(screen.getByRole("button", { name: "Reset" }));
    expect(onReset).toHaveBeenCalled();

    fireEvent.click(screen.getByRole("button", { name: /Filter/ }));
    expect(onFilter).toHaveBeenCalledWith("john");
  });

  it("handles non-Input widget onChange branch", () => {
    mockGetWidgetCls.mockReturnValue([
      ({ onChange }: { onChange: (v: string) => void }) => (
        <button type="button" onClick={() => onChange("direct")}>
          custom-change
        </button>
      ),
      {},
    ]);

    const onFilter = vi.fn();
    const onReset = vi.fn();
    render(
      <FilterColumn
        widgetType={EFieldWidgetType.Select}
        value=""
        onFilter={onFilter}
        onReset={onReset}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "custom-change" }));
    fireEvent.click(screen.getByRole("button", { name: /Filter/ }));
    expect(onFilter).toHaveBeenCalledWith("direct");
  });
});
