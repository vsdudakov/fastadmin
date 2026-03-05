import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import type React from "react";
import { afterEach, describe, expect, test, vi } from "vitest";

import { ConfigurationContext } from "@/providers/ConfigurationProvider";

vi.mock("@/components/crud-container", () => ({
  CrudContainer: ({
    children,
    title,
  }: {
    children: React.ReactNode;
    title: string;
  }) => (
    <div>
      <div>{title}</div>
      {children}
    </div>
  ),
}));

vi.mock("@/components/dashboard-action-widget", () => ({
  DashboardActionWidget: ({
    modelName,
    widgetAction,
  }: {
    modelName: string;
    widgetAction: { title: string };
  }) => (
    <div data-testid={`widget-${modelName}-${widgetAction.title}`}>
      {widgetAction.title}
    </div>
  ),
}));

vi.mock("@/components/dashboard-chart-widget", () => ({
  DashboardChartWidget: ({
    modelName,
    widgetAction,
  }: {
    modelName: string;
    widgetAction: { title: string };
  }) => (
    <div data-testid={`widget-${modelName}-${widgetAction.title}`}>
      {widgetAction.title}
    </div>
  ),
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

vi.mock("antd", () => ({
  theme: {
    useToken: () => ({
      token: {
        colorPrimary: "#000",
        colorBgContainer: "#fff",
        colorTextBase: "#000",
        colorBgBase: "#fff",
      },
    }),
  },
  Row: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Col: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Empty: ({ description }: { description: string }) => <div>{description}</div>,
  Input: ({
    value,
    onChange,
    placeholder,
  }: {
    value?: string;
    onChange?: (event: { target: { value: string } }) => void;
    placeholder?: string;
  }) => (
    <input
      value={value}
      placeholder={placeholder}
      onChange={(event) =>
        onChange?.({ target: { value: event.target.value } })
      }
    />
  ),
  Tabs: ({
    items,
    tabBarExtraContent,
  }: {
    items: Array<{ key: string; children: React.ReactNode }>;
    tabBarExtraContent?: { right?: React.ReactNode };
  }) => (
    <div>
      <div>{tabBarExtraContent?.right}</div>
      {items.map((item) => (
        <div key={item.key}>{item.children}</div>
      ))}
    </div>
  ),
}));

describe("Index container", () => {
  afterEach(() => {
    cleanup();
  });

  test("renders empty state when no widgets configured", async () => {
    const { Index } = await import("./index");
    const mockConfig = {
      configuration: {
        site_name: "Admin",
        username_field: "username",
        models: [],
      },
    };
    render(
      <ConfigurationContext.Provider value={mockConfig as any}>
        <Index />
      </ConfigurationContext.Provider>,
    );
    expect(screen.getByText("No dashboard widgets configured")).toBeTruthy();
  });

  test("renders dashboard widget items branch", async () => {
    const { Index } = await import("./index");
    const mockConfig = {
      configuration: {
        site_name: "Admin",
        username_field: "username",
        models: [
          {
            name: "Order",
            permissions: [],
            actions: [],
            fields: [],
            widget_actions: [
              {
                name: "sales_chart",
                title: "Orders",
                widget_action_type: "Action",
              },
            ],
          },
        ],
      },
    };
    render(
      <ConfigurationContext.Provider value={mockConfig as any}>
        <Index />
      </ConfigurationContext.Provider>,
    );
    expect(screen.getByTestId("widget-Order-Orders")).toBeTruthy();
  });

  test("filters dashboard widgets by widget title from search input", async () => {
    const { Index } = await import("./index");
    const mockConfig = {
      configuration: {
        site_name: "Admin",
        username_field: "username",
        models: [
          {
            name: "Order",
            permissions: [],
            actions: [],
            fields: [],
            widget_actions: [
              {
                name: "orders_chart",
                title: "Orders",
                tab: "Sales",
                widget_action_type: "Action",
              },
            ],
          },
          {
            name: "User",
            permissions: [],
            actions: [],
            fields: [],
            widget_actions: [
              {
                name: "users_chart",
                title: "Users",
                tab: "Marketing",
                widget_action_type: "Action",
              },
            ],
          },
        ],
      },
    };

    render(
      <ConfigurationContext.Provider value={mockConfig as any}>
        <Index />
      </ConfigurationContext.Provider>,
    );

    expect(screen.getByTestId("widget-Order-Orders")).toBeTruthy();
    expect(screen.getByTestId("widget-User-Users")).toBeTruthy();

    const searchInput = screen.getByPlaceholderText("Search widgets");
    fireEvent.change(searchInput, { target: { value: "orders" } });

    expect(screen.getByTestId("widget-Order-Orders")).toBeTruthy();
    expect(screen.queryByTestId("widget-User-Users")).toBeNull();
  });
});
