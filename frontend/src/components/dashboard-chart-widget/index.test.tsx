import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { ConfigProvider, Input } from "antd";
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  EDashboardWidgetType,
  EFieldWidgetType,
  type IModelWidgetAction,
  type IWidgetActionResponse,
} from "@/interfaces/configuration";

const {
  mockUseQuery,
  mockPostFetcher,
  mockGetWidgetCls,
  mockTransformValueToServer,
  lineChartSpy,
} = vi.hoisted(() => ({
  mockUseQuery: vi.fn(),
  mockPostFetcher: vi.fn(),
  mockGetWidgetCls: vi.fn(),
  mockTransformValueToServer: vi.fn((value: unknown) =>
    value ? `to-${String(value)}` : value,
  ),
  lineChartSpy: vi.fn(),
}));

vi.mock("@tanstack/react-query", () => ({
  useQuery: (options: unknown) => mockUseQuery(options),
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

import { DashboardChartWidget } from "./index";

const baseWidget: IModelWidgetAction = {
  name: "sales_chart",
  title: "Orders",
  description: undefined,
  tab: "Analytics",
  widget_action_type: EDashboardWidgetType.ChartLine,
  widget_action_props: {
    x_field: "day",
    y_field: "count",
  },
};

const renderWidget = (widgetAction: IModelWidgetAction) =>
  render(
    <ConfigProvider>
      <DashboardChartWidget modelName="Order" widgetAction={widgetAction} />
    </ConfigProvider>,
  );

describe("DashboardWidget", () => {
  afterEach(() => {
    cleanup();
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
        data: [{ day: "Mon", count: 2 }],
      } as IWidgetActionResponse,
    });
    mockGetWidgetCls.mockReturnValue([Input, {}]);

    renderWidget({
      ...baseWidget,
      widget_action_filters: [
        {
          field_name: "created_at",
          widget_type: EFieldWidgetType.Input,
          widget_props: { "data-testid": "range-input" },
        },
      ],
    });

    expect(screen.getAllByTestId("line-chart").length).toBeGreaterThan(0);
    expect(lineChartSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        xField: "day",
        yField: "count",
      }),
    );

    expect(mockUseQuery).toHaveBeenCalledWith(
      expect.objectContaining({
        queryKey: expect.arrayContaining([
          "/widget-action",
          "Order",
          "sales_chart",
        ]),
        refetchOnWindowFocus: false,
        queryFn: expect.any(Function),
      }),
    );
  });

  it("passes series field for multi-series charts", () => {
    mockUseQuery.mockReturnValue({
      isLoading: false,
      data: {
        data: [
          { day: "Mon", count: 2, status: "paid" },
          { day: "Mon", count: 1, status: "pending" },
        ],
      } as IWidgetActionResponse,
    });

    renderWidget({
      ...baseWidget,
      widget_action_props: {
        x_field: "day",
        y_field: "count",
        series_field: "status",
      },
    });

    expect(screen.getAllByTestId("line-chart").length).toBeGreaterThan(0);
    expect(lineChartSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        xField: "day",
        yField: "count",
        seriesField: "status",
        colorField: "status",
      }),
    );
  });

  it("passes custom series colors for multi-series charts", () => {
    mockUseQuery.mockReturnValue({
      isLoading: false,
      data: {
        data: [
          { day: "Mon", count: 2, status: "paid" },
          { day: "Mon", count: 1, status: "pending" },
        ],
      } as IWidgetActionResponse,
    });

    renderWidget({
      ...baseWidget,
      widget_action_props: {
        x_field: "day",
        y_field: "count",
        series_field: "status",
        series_color: ["#22c55e", "#f59e0b"],
      },
    });

    expect(lineChartSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        seriesField: "status",
        colorField: "status",
        color: ["#22c55e", "#f59e0b"],
      }),
    );
  });

  it("applies and resets filters, toggling active state", async () => {
    mockUseQuery.mockReturnValue({
      isLoading: false,
      data: {
        data: [{ day: "Mon", count: 2 }],
      } as IWidgetActionResponse,
    });
    mockGetWidgetCls.mockReturnValue([Input, { "data-testid": "range-input" }]);

    renderWidget({
      ...baseWidget,
      widget_action_filters: [
        {
          field_name: "created_at",
          widget_type: EFieldWidgetType.Input,
          widget_props: { "data-testid": "range-input" },
        },
      ],
    });

    const filtersButton = screen.getAllByRole("button", {
      name: /Filters/i,
    })[0];
    expect(filtersButton.className).not.toContain("ant-btn-primary");

    fireEvent.click(filtersButton);

    const inputs = await screen.findAllByTestId("range-input");
    fireEvent.change(inputs[0], { target: { value: "2026-01-05" } });

    fireEvent.click(screen.getByRole("button", { name: /Apply/i }));

    await waitFor(() => {
      expect(filtersButton.className).toContain("ant-btn-primary");
      expect(filtersButton.className).toContain("ant-btn-dangerous");
    });

    fireEvent.click(filtersButton);
    fireEvent.click(screen.getByRole("button", { name: /Reset/i }));

    await waitFor(() => {
      expect(filtersButton.className).not.toContain("ant-btn-primary");
    });
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
      data: { data: [] } as IWidgetActionResponse,
    });
    mockGetWidgetCls.mockReturnValue([
      CustomWidget,
      { "data-testid": "custom-filter" },
    ]);

    renderWidget({
      ...baseWidget,
      widget_action_filters: [
        {
          field_name: "status",
          widget_type: EFieldWidgetType.Select,
          widget_props: { "data-testid": "custom-filter" },
        },
      ],
    });

    fireEvent.click(screen.getAllByRole("button", { name: /Filters/i })[0]);

    const customButtons = screen.getAllByRole("button", { name: /Custom/i });
    fireEvent.click(customButtons[0]);

    await waitFor(() => {
      expect(mockGetWidgetCls).toHaveBeenCalled();
    });
  });
});
