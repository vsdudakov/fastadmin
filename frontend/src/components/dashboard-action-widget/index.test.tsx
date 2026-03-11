import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { ConfigProvider, Input, message } from "antd";
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  EDashboardWidgetType,
  EFieldWidgetType,
  type IModelWidgetAction,
  type IWidgetActionResponse,
} from "@/interfaces/configuration";

const { mockPostFetcher, mockGetWidgetCls, mockTransformValueToServer } =
  vi.hoisted(() => ({
    mockPostFetcher: vi.fn(),
    mockGetWidgetCls: vi.fn(),
    mockTransformValueToServer: vi.fn((value: unknown) =>
      value ? `to-${String(value)}` : value,
    ),
  }));

vi.mock("@/fetchers/fetchers", () => ({
  postFetcher: (url: string, payload: unknown) => mockPostFetcher(url, payload),
}));

vi.mock("@/helpers/widgets", () => ({
  getWidgetCls: (...args: unknown[]) => mockGetWidgetCls(...args),
}));

vi.mock("@/helpers/transform", () => ({
  transformValueToServer: (value: unknown) => mockTransformValueToServer(value),
}));

vi.mock("@/helpers/title", () => ({
  getTitleFromFieldName: (value: string) => `title-${value}`,
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

import type { MessageType } from "antd/es/message/interface";
import {
  areWidgetValuesEqual,
  buildWidgetActionQuery,
  DashboardActionWidget,
  hasWidgetValue,
  isWidgetActionArgumentVisible,
} from "./index";

const baseWidget: IModelWidgetAction = {
  name: "sales_chart",
  title: "Orders",
  description: undefined,
  tab: "Analytics",
  widget_action_type: EDashboardWidgetType.Action,
};

const renderWidget = (widgetAction: IModelWidgetAction) =>
  render(
    <ConfigProvider>
      <DashboardActionWidget modelName="Order" widgetAction={widgetAction} />
    </ConfigProvider>,
  );

describe("DashboardWidget", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("renders action widget without filters when none configured", () => {
    const { container } = renderWidget(baseWidget);

    expect(screen.queryByRole("button", { name: /Filters/i })).toBeNull();
    expect(screen.getByRole("button", { name: /Run Action/i })).toBeTruthy();
    expect(container.querySelector("pre")).toBeNull();
  });

  it("renders info tooltip icon when description is provided", () => {
    renderWidget({
      ...baseWidget,
      description: "Helpful context",
    });

    expect(document.querySelector('[data-icon="info-circle"]')).toBeTruthy();
  });

  it("runs action and configures payload with API filter values", async () => {
    mockGetWidgetCls.mockReturnValue([Input, {}]);
    mockPostFetcher.mockResolvedValue({
      data: [{ created_at: "2026-01-05" }],
    } as IWidgetActionResponse);

    renderWidget({
      ...baseWidget,
      widget_action_props: {
        arguments: [
          {
            name: "created_at",
            widget_type: EFieldWidgetType.Input,
            widget_props: { "data-testid": "range-input" },
          },
        ],
      },
    } as IModelWidgetAction);

    const inputs = screen.getAllByTestId("range-input");
    fireEvent.change(inputs[0], { target: { value: "2026-01-05" } });

    // run action (use getAllByRole when multiple widgets may render)
    fireEvent.click(screen.getAllByRole("button", { name: /Run/i })[0]);

    await waitFor(() => {
      expect(mockPostFetcher).toHaveBeenCalledWith(
        "/widget-action/Order/sales_chart",
        expect.objectContaining({
          query: expect.any(Array),
        }),
      );

      // results rendered with search and copy controls
      expect(screen.getByPlaceholderText("Search results")).toBeDefined();
      expect(screen.getByRole("button", { name: /Copy/i })).toBeDefined();
    });
  });

  it("filters results, supports reset and copy to clipboard", async () => {
    mockGetWidgetCls.mockReturnValue([Input, {}]);
    mockPostFetcher.mockResolvedValue({
      data: [
        { id: 1, name: "alpha" },
        { id: 2, name: "beta" },
      ],
    } as IWidgetActionResponse);

    const originalNavigator = globalThis.navigator;
    const clipboardWrite = vi.fn();
    (globalThis as unknown as { navigator: Navigator }).navigator = {
      ...originalNavigator,
      clipboard: { writeText: clipboardWrite },
    } as unknown as Navigator;
    const messageSpy = vi
      .spyOn(message, "success")
      .mockImplementation(() => "success" as unknown as MessageType);

    renderWidget({
      ...baseWidget,
      widget_action_props: {
        arguments: [
          {
            name: "created_at",
            widget_type: EFieldWidgetType.Input,
            widget_props: { "data-testid": "range-input" },
          },
        ],
      },
    } as IModelWidgetAction);

    const inputs = screen.getAllByTestId("range-input");
    fireEvent.change(inputs[0], { target: { value: "2026-01-05" } });

    const runButton = screen.getAllByRole("button", {
      name: /Run Action/i,
    })[0];
    fireEvent.click(runButton);

    const searchInput = await screen.findByPlaceholderText("Search results");
    fireEvent.change(searchInput, { target: { value: "beta" } });
    fireEvent.click(screen.getByRole("button", { name: /search/i }));

    fireEvent.click(screen.getByRole("button", { name: /Copy/i }));

    await waitFor(() => {
      expect(clipboardWrite).toHaveBeenCalledTimes(1);
      expect(messageSpy).toHaveBeenCalledWith("Results copied to clipboard");
    });

    fireEvent.click(screen.getByRole("button", { name: /Reset/i }));

    await waitFor(() => {
      expect(screen.queryByRole("button", { name: /Copy/i })).toBeNull();
    });

    (globalThis as any).navigator = originalNavigator;
    messageSpy.mockRestore();
  }, 10000);

  it("copies filtered results again after search", async () => {
    mockGetWidgetCls.mockReturnValue([Input, {}]);
    mockPostFetcher.mockResolvedValue({
      data: [
        { id: 1, name: "alpha" },
        { id: 2, name: "beta" },
      ],
    } as IWidgetActionResponse);

    const originalNavigator = globalThis.navigator;
    const clipboardWrite = vi.fn();
    (globalThis as unknown as { navigator: Navigator }).navigator = {
      ...originalNavigator,
      clipboard: { writeText: clipboardWrite },
    } as unknown as Navigator;

    const messageSpy = vi
      .spyOn(message, "success")
      .mockImplementation(() => "success" as unknown as MessageType);

    renderWidget({
      ...baseWidget,
      widget_action_props: {
        arguments: [
          {
            name: "created_at",
            widget_type: EFieldWidgetType.Input,
            widget_props: { "data-testid": "range-input" },
          },
        ],
      },
    } as IModelWidgetAction);

    const inputs = screen.getAllByTestId("range-input");
    fireEvent.change(inputs[0], { target: { value: "2026-01-05" } });

    fireEvent.click(
      screen.getAllByRole("button", {
        name: /Run Action/i,
      })[0],
    );

    const searchInput = await screen.findByPlaceholderText("Search results");
    fireEvent.change(searchInput, { target: { value: "beta" } });
    fireEvent.click(screen.getByRole("button", { name: /search/i }));

    // copy filtered results again
    fireEvent.click(screen.getByRole("button", { name: /Copy/i }));

    await waitFor(() => {
      expect(clipboardWrite).toHaveBeenCalledTimes(1);
      expect(messageSpy).toHaveBeenCalledWith("Results copied to clipboard");
    });

    (globalThis as any).navigator = originalNavigator;
    messageSpy.mockRestore();
  });

  it("handles default widget onChange branch", async () => {
    const CustomWidget = ({
      onChange,
      ...props
    }: {
      onChange: (value: string) => void;
      [key: string]: unknown;
    }) => (
      <button
        type="button"
        data-testid={String(props["data-testid"])}
        onClick={() => onChange("direct-value")}
      >
        Custom
      </button>
    );

    mockPostFetcher.mockResolvedValue({ data: [] } as IWidgetActionResponse);
    mockGetWidgetCls.mockReturnValue([
      CustomWidget,
      { "data-testid": "custom-filter" },
    ]);

    renderWidget({
      ...baseWidget,
      widget_action_props: {
        arguments: [
          {
            name: "status",
            widget_type: EFieldWidgetType.Select,
            widget_props: { "data-testid": "custom-filter" },
          },
        ],
      },
    } as IModelWidgetAction);

    const customButtons = screen.getAllByTestId("custom-filter");
    fireEvent.click(customButtons[0]);

    fireEvent.click(screen.getAllByRole("button", { name: /Run/i })[0]);

    await waitFor(() => {
      expect(mockPostFetcher).toHaveBeenCalledWith(
        "/widget-action/Order/sales_chart",
        expect.objectContaining({
          query: expect.any(Array),
        }),
      );
    });
  });

  it("sends empty query for unset optional argument", async () => {
    mockGetWidgetCls.mockReturnValue([Input, {}]);
    mockPostFetcher.mockResolvedValue({ data: [] } as IWidgetActionResponse);

    renderWidget({
      ...baseWidget,
      widget_action_props: {
        arguments: [
          {
            name: "created_at",
            widget_type: EFieldWidgetType.Input,
            widget_props: { "data-testid": "range-input" },
          },
        ],
      },
    } as IModelWidgetAction);

    fireEvent.click(screen.getAllByRole("button", { name: /Run Action/i })[0]);

    await waitFor(() => {
      expect(mockPostFetcher).toHaveBeenCalledWith(
        "/widget-action/Order/sales_chart",
        expect.objectContaining({
          query: [],
        }),
      );
    });
  });

  it("shows child argument only when parent value matches", () => {
    const typeArgument = {
      name: "type",
      widget_type: EFieldWidgetType.Input,
    };
    const salesDateArgument = {
      name: "sales_date",
      widget_type: EFieldWidgetType.DatePicker,
      parent_argument: {
        name: "type",
        value: "sales",
      },
    };
    const revenueDateArgument = {
      name: "revenue_date",
      widget_type: EFieldWidgetType.DatePicker,
      parent_argument: {
        name: "type",
        value: "revenue",
      },
    };
    const allArguments = [typeArgument, salesDateArgument, revenueDateArgument];

    const salesValues = { type: "sales", sales_date: "2026-01-05" };
    const salesVisibleArguments = allArguments.filter((argument) =>
      isWidgetActionArgumentVisible(argument, salesValues),
    );

    expect(salesVisibleArguments).toEqual([typeArgument, salesDateArgument]);
    expect(buildWidgetActionQuery(salesVisibleArguments, salesValues)).toEqual([
      {
        field_name: "type",
        widget_type: EFieldWidgetType.Input,
        value: "to-sales",
      },
      {
        field_name: "sales_date",
        widget_type: EFieldWidgetType.DatePicker,
        value: "to-2026-01-05",
      },
    ]);

    const revenueValues = { type: "revenue", revenue_date: "2026-01-06" };
    const revenueVisibleArguments = allArguments.filter((argument) =>
      isWidgetActionArgumentVisible(argument, revenueValues),
    );

    expect(revenueVisibleArguments).toEqual([
      typeArgument,
      revenueDateArgument,
    ]);
    expect(
      buildWidgetActionQuery(revenueVisibleArguments, revenueValues),
    ).toEqual([
      {
        field_name: "type",
        widget_type: EFieldWidgetType.Input,
        value: "to-revenue",
      },
      {
        field_name: "revenue_date",
        widget_type: EFieldWidgetType.DatePicker,
        value: "to-2026-01-06",
      },
    ]);
  });

  it("matches parent values for object-like data", () => {
    expect(
      areWidgetValuesEqual(
        { from: "2026-01-01", to: "2026-01-31" },
        { from: "2026-01-01", to: "2026-01-31" },
      ),
    ).toBe(true);
    expect(areWidgetValuesEqual(["a", "b"], ["a", "b"])).toBe(true);
    expect(areWidgetValuesEqual(["a", "b"], ["a", "c"])).toBe(false);
  });

  it("areWidgetValuesEqual returns false when JSON.stringify throws", () => {
    const circular: Record<string, unknown> = {};
    circular.self = circular;
    expect(areWidgetValuesEqual(circular, {})).toBe(false);
  });

  it("hasWidgetValue covers null, string and array branches", () => {
    expect(hasWidgetValue(undefined)).toBe(false);
    expect(hasWidgetValue(null)).toBe(false);
    expect(hasWidgetValue("   ")).toBe(false);
    expect(hasWidgetValue(["x"])).toBe(true);
  });

  it("buildWidgetActionQuery filters blank string and keeps array value", () => {
    const query = buildWidgetActionQuery(
      [
        { name: "name", widget_type: EFieldWidgetType.Input },
        { name: "tags", widget_type: EFieldWidgetType.Select },
      ],
      { name: "   ", tags: ["a", "b"] },
    );

    expect(query).toEqual([
      {
        field_name: "tags",
        widget_type: EFieldWidgetType.Select,
        value: "to-a,b",
      },
    ]);
  });
});
