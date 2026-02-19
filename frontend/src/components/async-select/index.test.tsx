import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { ConfigProvider } from "antd";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { EModelPermission } from "@/interfaces/configuration";
import { ConfigurationContext } from "@/providers/ConfigurationProvider";
import { AsyncSelect } from "./index";

const { mockGetFetcher, mockPostFetcher, mockPatchFetcher } = vi.hoisted(
  () => ({
    mockGetFetcher: vi.fn(),
    mockPostFetcher: vi.fn(),
    mockPatchFetcher: vi.fn(),
  }),
);

vi.mock("@/fetchers/fetchers", () => ({
  getFetcher: (url: string) => mockGetFetcher(url),
  postFetcher: (url: string, payload: unknown) => mockPostFetcher(url, payload),
  patchFetcher: (url: string, payload: unknown) =>
    mockPatchFetcher(url, payload),
  deleteFetcher: vi.fn(),
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

const mockModel = {
  name: "test",
  permissions: [EModelPermission.Add, EModelPermission.Change],
  actions: [],
  fields: [
    {
      name: "name",
      add_configuration: { form_widget_type: "Input" },
      change_configuration: { form_widget_type: "Input" },
    },
  ],
  fieldsets: [[undefined, { fields: ["name"] }]],
  verbose_name: "Test",
};

const mockConfig = {
  configuration: {
    site_name: "Admin",
    username_field: "username",
    models: [mockModel],
    dashboard_widgets: [],
  },
};

describe("AsyncSelect", () => {
  const renderWithProviders = (ui: ReactNode) => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });

    return render(
      <QueryClientProvider client={queryClient}>
        <ConfigProvider>{ui}</ConfigProvider>
      </QueryClientProvider>,
    );
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockGetFetcher.mockImplementation((url: string) => {
      if (url.includes("/list/")) {
        return Promise.resolve({
          results: [
            { id: 1, name: "Item 1" },
            { id: 2, name: "Item 2" },
          ],
        });
      }
      if (url.includes("/retrieve/")) {
        return Promise.resolve({ id: 1, name: "Item 1" });
      }
      return Promise.resolve({ results: [] });
    });
    mockPostFetcher.mockResolvedValue({});
    mockPatchFetcher.mockResolvedValue({});
  });

  it("renders and loads options from list API", async () => {
    renderWithProviders(
      <ConfigurationContext.Provider value={mockConfig as any}>
        <AsyncSelect idField="id" labelFields={["name"]} parentModel="test" />
      </ConfigurationContext.Provider>,
    );
    await waitFor(() => {
      expect(mockGetFetcher).toHaveBeenCalledWith(
        expect.stringContaining("/list/test"),
      );
    });
  });

  it("opens Add modal when Add button is clicked", async () => {
    const { container } = renderWithProviders(
      <ConfigurationContext.Provider value={mockConfig as any}>
        <AsyncSelect idField="id" labelFields={["name"]} parentModel="test" />
      </ConfigurationContext.Provider>,
    );
    await waitFor(() => {
      expect(mockGetFetcher).toHaveBeenCalled();
    });
    const addBtn = container.querySelector("button");
    expect(addBtn).toBeTruthy();
    if (addBtn) {
      fireEvent.click(addBtn);
      expect(screen.getByRole("dialog")).toBeTruthy();
    }
  });

  it("opens Change modal and fetches retrieve when value is set and Edit clicked", async () => {
    const { container } = renderWithProviders(
      <ConfigurationContext.Provider value={mockConfig as any}>
        <AsyncSelect
          idField="id"
          labelFields={["name"]}
          parentModel="test"
          value={1}
        />
      </ConfigurationContext.Provider>,
    );
    await waitFor(() => {
      expect(mockGetFetcher).toHaveBeenCalled();
    });
    const buttons = container.querySelectorAll("button");
    expect(buttons.length).toBeGreaterThanOrEqual(2);
    fireEvent.click(buttons[1]);
    await waitFor(() => {
      expect(mockGetFetcher).toHaveBeenCalledWith(
        expect.stringMatching(/\/retrieve\/test\/1/),
      );
    });
  });

  it("renders with onChange callback", async () => {
    const onChange = vi.fn();
    const { container } = renderWithProviders(
      <ConfigurationContext.Provider value={mockConfig as any}>
        <AsyncSelect
          idField="id"
          labelFields={["name"]}
          parentModel="test"
          onChange={onChange}
        />
      </ConfigurationContext.Provider>,
    );
    await waitFor(() => {
      expect(mockGetFetcher).toHaveBeenCalled();
    });
    expect(container).toBeTruthy();
  });

  it("renders in multiple mode with array value", async () => {
    const onChange = vi.fn();
    renderWithProviders(
      <ConfigurationContext.Provider value={mockConfig as any}>
        <AsyncSelect
          idField="id"
          labelFields={["name"]}
          parentModel="test"
          {...({ mode: "multiple" } as any)}
          value={[1, 2]}
          onChange={onChange}
        />
      </ConfigurationContext.Provider>,
    );
    await waitFor(() => {
      expect(mockGetFetcher).toHaveBeenCalledWith(
        expect.stringContaining("/list/test"),
      );
    });
  });

  it("shows Empty when model has no Add permission", async () => {
    const configNoAdd = {
      configuration: {
        ...mockConfig.configuration,
        models: [
          {
            ...mockModel,
            permissions: [EModelPermission.Change],
          },
        ],
      },
    };
    const { container } = renderWithProviders(
      <ConfigurationContext.Provider value={configNoAdd as any}>
        <AsyncSelect idField="id" labelFields={["name"]} parentModel="test" />
      </ConfigurationContext.Provider>,
    );
    await waitFor(() => {
      expect(mockGetFetcher).toHaveBeenCalled();
    });
    const addBtn = container.querySelector("button");
    if (addBtn) {
      fireEvent.click(addBtn);
      expect(screen.getByText(/No permissions for model/i)).toBeTruthy();
    }
  });
});
