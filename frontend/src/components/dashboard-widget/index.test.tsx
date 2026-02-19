import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { ConfigProvider, Input } from "antd";
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  EDashboardWidgetType,
  EFieldWidgetType,
  type IDashboardWidget,
} from "@/interfaces/configuration";

const {
  mockUseQuery,
  mockGetFetcher,
  mockGetWidgetCls,
  mockTransformValueFromServer,
  mockTransformValueToServer,
  lineChartSpy,
} = vi.hoisted(() => ({
  mockUseQuery: vi.fn(),
  mockGetFetcher: vi.fn(),
  mockGetWidgetCls: vi.fn(),
  mockTransformValueFromServer: vi.fn((value: unknown) =>
    value ? `from-${String(value)}` : value,
  ),
  mockTransformValueToServer: vi.fn((value: unknown) =>
    value ? `to-${String(value)}` : value,
  ),
  lineChartSpy: vi.fn(),
}));

vi.mock("@tanstack/react-query", () => ({
  useQuery: (options: unknown) => mockUseQuery(options),
}));

vi.mock("@/fetchers/fetchers", () => ({
  getFetcher: (url: string) => mockGetFetcher(url),
}));

vi.mock("@/helpers/widgets", () => ({
  getWidgetCls: (...args: unknown[]) => mockGetWidgetCls(...args),
}));

vi.mock("@/helpers/transform", () => ({
  transformValueFromServer: (value: unknown) =>
    mockTransformValueFromServer(value),
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

vi.mock("@ant-design/charts", () => ({
  Line: (props: Record<string, unknown>) => {
    lineChartSpy(props);
    return <div data-testid="line-chart" />;
  },
  Area: () => <div data-testid="area-chart" />,
  Column: () => <div data-testid="column-chart" />,
  Bar: () => <div data-testid="bar-chart" />,
  Pie: () => <div data-testid="pie-chart" />,
}));

import { DashboardWidget } from "./index";

const baseWidget: IDashboardWidget = {
  key: "orders",
  title: "Orders",
  dashboard_widget_type: EDashboardWidgetType.ChartLine,
  dashboard_widget_props: {},
  x_field: "day",
  y_field: "count",
};

const renderWidget = (widget: IDashboardWidget) =>
  render(
    <ConfigProvider>
      <DashboardWidget widget={widget} />
    </ConfigProvider>,
  );

describe("DashboardWidget", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("renders a loading state", () => {
    mockUseQuery.mockReturnValue({
      isLoading: true,
      data: undefined,
    });

    const { container } = renderWidget(baseWidget);
    expect(container.querySelector(".ant-spin")).toBeTruthy();
    expect(screen.queryByTestId("line-chart")).toBeNull();
  });

  it("renders line chart and configures query with API filter values", async () => {
    mockUseQuery.mockReturnValue({
      isLoading: false,
      data: {
        min_x_field: "2026-01-01",
        max_x_field: "2026-01-31",
        period_x_field: "week",
        results: [{ day: "Mon", count: 2 }],
      },
    });
    mockGetWidgetCls.mockReturnValue([Input, {}]);

    renderWidget({
      ...baseWidget,
      x_field_filter_widget_type: EFieldWidgetType.Input,
      x_field_periods: ["day", "week"],
      x_field_filter_widget_props: { "data-testid": "range-input" },
    });

    expect(screen.getByTestId("line-chart")).toBeTruthy();
    expect(lineChartSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        xField: "day",
        yField: "count",
      }),
    );

    const inputs = screen.getAllByTestId("range-input");
    fireEvent.change(inputs[0], { target: { value: "2026-01-05" } });

    await waitFor(() => {
      expect(mockTransformValueToServer).toHaveBeenCalledWith("2026-01-05");
    });

    expect(mockUseQuery).toHaveBeenCalledWith(
      expect.objectContaining({
        queryKey: expect.arrayContaining(["/dashboard-widget", "orders"]),
        refetchOnWindowFocus: false,
        queryFn: expect.any(Function),
      }),
    );

    const queryOptions = mockUseQuery.mock.calls[0][0] as {
      queryFn: () => Promise<unknown>;
    };
    await queryOptions.queryFn();
    expect(mockGetFetcher).toHaveBeenCalledWith(
      expect.stringContaining("/dashboard-widget/orders?"),
    );
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

    mockUseQuery.mockReturnValue({
      isLoading: false,
      data: { results: [] },
    });
    mockGetWidgetCls.mockReturnValue([
      CustomWidget,
      { "data-testid": "custom-filter" },
    ]);

    renderWidget({
      ...baseWidget,
      x_field_filter_widget_type: EFieldWidgetType.Select,
    });

    const customButtons = screen.getAllByTestId("custom-filter");
    fireEvent.click(customButtons[0]);

    await waitFor(() => {
      expect(mockTransformValueToServer).toHaveBeenCalledWith("direct-value");
    });
  });
});
