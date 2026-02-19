import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  ConfigurationContext,
  defaultConfiguration,
} from "@/providers/ConfigurationProvider";

const { mockUseQuery, mockGetFetcher } = vi.hoisted(() => ({
  mockUseQuery: vi.fn(),
  mockGetFetcher: vi.fn(),
}));

vi.mock("@tanstack/react-query", () => ({
  useQuery: (options: unknown) => mockUseQuery(options),
}));

vi.mock("@/fetchers/fetchers", () => ({
  getFetcher: (url: string) => mockGetFetcher(url),
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

import { ConfigurationProvider } from "./provider";

const ContextReader = () => (
  <ConfigurationContext.Consumer>
    {({ configuration }) => (
      <div data-testid="configuration">{configuration.site_name}</div>
    )}
  </ConfigurationContext.Consumer>
);

describe("ConfigurationProvider", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("returns null while loading", () => {
    mockUseQuery.mockReturnValue({
      isLoading: true,
      error: null,
    });

    render(
      <ConfigurationProvider>
        <div data-testid="child">child</div>
      </ConfigurationProvider>,
    );

    expect(screen.queryByTestId("child")).toBeNull();
  });

  it("renders warning result when configuration query fails", () => {
    mockUseQuery.mockReturnValue({
      isLoading: false,
      error: {
        response: { data: { exception: "Invalid model mapping" } },
        message: "Request failed",
      },
      data: undefined,
    });

    render(
      <ConfigurationProvider>
        <div>ignored</div>
      </ConfigurationProvider>,
    );

    expect(
      screen.getByText(
        "Invalid configuration. Please check your admin model classes and logs.",
      ),
    ).toBeTruthy();
    expect(screen.getByText("Show Error")).toBeTruthy();
  });

  it("renders warning result with message fallback when no exception is present", () => {
    mockUseQuery.mockReturnValue({
      isLoading: false,
      error: {
        message: "Network timeout",
      },
      data: undefined,
    });

    render(
      <ConfigurationProvider>
        <div>ignored</div>
      </ConfigurationProvider>,
    );

    expect(
      screen.getByText(
        "Invalid configuration. Please check your admin model classes and logs.",
      ),
    ).toBeTruthy();
  });

  it("provides fetched configuration and uses expected query options", async () => {
    mockUseQuery.mockReturnValue({
      isLoading: false,
      error: null,
      data: {
        site_name: "My Admin",
        username_field: "email",
        models: [],
        dashboard_widgets: [],
      },
    });

    render(
      <ConfigurationProvider>
        <ContextReader />
      </ConfigurationProvider>,
    );

    expect(screen.getByTestId("configuration").textContent).toBe("My Admin");
    expect(mockUseQuery).toHaveBeenCalledWith(
      expect.objectContaining({
        queryKey: ["/configuration"],
        retry: false,
        refetchOnWindowFocus: false,
        queryFn: expect.any(Function),
      }),
    );

    const useQueryOptions = mockUseQuery.mock.calls[0][0] as {
      queryFn: () => Promise<unknown>;
    };
    await useQueryOptions.queryFn();
    expect(mockGetFetcher).toHaveBeenCalledWith("/configuration");
  });

  it("falls back to default configuration when query has no data", () => {
    mockUseQuery.mockReturnValue({
      isLoading: false,
      error: null,
      data: undefined,
    });

    render(
      <ConfigurationProvider>
        <ContextReader />
      </ConfigurationProvider>,
    );

    expect(screen.getByTestId("configuration").textContent).toBe(
      defaultConfiguration.site_name,
    );
  });
});
