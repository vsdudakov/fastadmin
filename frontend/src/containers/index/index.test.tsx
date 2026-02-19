import { cleanup, render, screen } from "@testing-library/react";
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

vi.mock("@/components/dashboard-widget", () => ({
  DashboardWidget: ({ widget }: { widget: { title: string } }) => (
    <div data-testid={`widget-${widget.title}`}>{widget.title}</div>
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
  Row: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Col: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Empty: ({ description }: { description: string }) => <div>{description}</div>,
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
        dashboard_widgets: [],
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
        models: [],
        dashboard_widgets: [
          {
            title: "Orders",
            model: "order",
            list_display: "id",
          },
        ],
      },
    };
    render(
      <ConfigurationContext.Provider value={mockConfig as any}>
        <Index />
      </ConfigurationContext.Provider>,
    );
    expect(screen.getByTestId("widget-Orders")).toBeTruthy();
  });
});
