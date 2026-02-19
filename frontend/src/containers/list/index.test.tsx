import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import type React from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { EModelPermission } from "@/interfaces/configuration";
import { ConfigurationContext } from "@/providers/ConfigurationProvider";
import { List } from "./index";

const {
  mockUseQuery,
  mockUseMutation,
  mockUseTableQuery,
  mockUseTableColumns,
  mockGetConfigurationModel,
  mockNavigate,
  mockSetFilters,
  mockSetPage,
  mockSetPageSize,
  mockMutateAction,
  mockMutateDelete,
  mockSetSearch,
  mockSetAction,
  mockResetTable,
  mockRefetch,
  mockMessageSuccess,
  mockMessageError,
  mockHandleError,
} = vi.hoisted(() => ({
  mockUseQuery: vi.fn(),
  mockUseMutation: vi.fn(),
  mockUseTableQuery: vi.fn(),
  mockUseTableColumns: vi.fn(),
  mockGetConfigurationModel: vi.fn(),
  mockNavigate: vi.fn(),
  mockSetFilters: vi.fn(),
  mockSetPage: vi.fn(),
  mockSetPageSize: vi.fn(),
  mockMutateAction: vi.fn(),
  mockMutateDelete: vi.fn(),
  mockSetSearch: vi.fn(),
  mockSetAction: vi.fn(),
  mockResetTable: vi.fn(),
  mockRefetch: vi.fn(),
  mockMessageSuccess: vi.fn(),
  mockMessageError: vi.fn(),
  mockHandleError: vi.fn(),
}));

vi.mock("@tanstack/react-query", () => ({
  useQuery: (options: unknown) => mockUseQuery(options),
  useMutation: (options: unknown) => mockUseMutation(options),
}));

vi.mock("react-router-dom", async () => {
  const actual =
    await vi.importActual<typeof import("react-router-dom")>(
      "react-router-dom",
    );
  return {
    ...actual,
    Link: ({ to, children }: { to: string; children: React.ReactNode }) => (
      <a href={to}>{children}</a>
    ),
    useNavigate: () => mockNavigate,
    useParams: () => ({ model: "user" }),
  };
});

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
  message: {
    success: (...args: unknown[]) => mockMessageSuccess(...args),
    error: (...args: unknown[]) => mockMessageError(...args),
  },
  Breadcrumb: ({ items }: { items: Array<{ title: React.ReactNode }> }) => (
    <div>
      {items.map((item, i) => (
        <span key={String(i)}>{item.title}</span>
      ))}
    </div>
  ),
  Row: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Col: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Empty: ({ description }: { description: string }) => <div>{description}</div>,
  Button: ({
    children,
    onClick,
    disabled,
  }: {
    children: React.ReactNode;
    onClick?: () => void;
    disabled?: boolean;
  }) => (
    <button type="button" onClick={onClick} disabled={disabled}>
      {children}
    </button>
  ),
  Input: {
    Search: ({ onSearch }: { onSearch?: (value: string) => void }) => (
      <button type="button" onClick={() => onSearch?.("term")}>
        Search
      </button>
    ),
  },
  Select: Object.assign(
    ({
      children,
      onChange,
    }: {
      children: React.ReactNode;
      onChange?: (v: string) => void;
    }) => (
      <div>
        <button type="button" onClick={() => onChange?.("bulk")}>
          choose-action
        </button>
        {children}
      </div>
    ),
    {
      Option: ({
        children,
        value,
      }: {
        children: React.ReactNode;
        value: string;
      }) => <div data-testid={`option-${value}`}>{children}</div>,
    },
  ),
}));

vi.mock("@/components/crud-container", () => ({
  CrudContainer: ({
    title,
    headerActions,
    bottomActions,
    children,
  }: {
    title: React.ReactNode;
    headerActions: React.ReactNode;
    bottomActions: React.ReactNode;
    children: React.ReactNode;
  }) => (
    <div>
      <div>{title}</div>
      <div data-testid="header-actions">{headerActions}</div>
      <div data-testid="bottom-actions">{bottomActions}</div>
      <div data-testid="content">{children}</div>
    </div>
  ),
}));

vi.mock("@/components/table-or-cards", () => ({
  TableOrCards: () => <div data-testid="table" />,
}));

vi.mock("@/components/export-btn", () => ({
  ExportBtn: () => <div>export-btn</div>,
}));

vi.mock("@/helpers/configuration", () => ({
  getConfigurationModel: (...args: unknown[]) =>
    mockGetConfigurationModel(...args),
}));

vi.mock("@/helpers/forms", () => ({
  handleError: (...args: unknown[]) => mockHandleError(...args),
}));

vi.mock("@/helpers/title", () => ({
  getTitleFromModel: (_m: unknown, plural?: boolean) =>
    plural ? "Users" : "User",
}));

vi.mock("@/helpers/transform", () => ({
  transformFiltersToServer: () => ({}),
}));

vi.mock("@/fetchers/fetchers", () => ({
  getFetcher: vi.fn(),
  postFetcher: vi.fn(),
  deleteFetcher: vi.fn(),
}));

vi.mock("@/hooks/useIsMobile", () => ({
  useIsMobile: () => false,
}));

vi.mock("@/hooks/useTableColumns", () => ({
  useTableColumns: (...args: unknown[]) => mockUseTableColumns(...args),
}));

vi.mock("@/hooks/useTableQuery", () => ({
  useTableQuery: (...args: unknown[]) => mockUseTableQuery(...args),
}));

describe("List container", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseQuery.mockReturnValue({
      data: { results: [{ id: "1" }], total: 1 },
      isLoading: false,
      refetch: mockRefetch,
    });
    let mutationHookCall = 0;
    mockUseMutation.mockImplementation(() => {
      const index = mutationHookCall % 2;
      mutationHookCall += 1;
      if (index === 0) {
        return { mutate: mockMutateDelete };
      }
      return { mutate: mockMutateAction, isPending: false };
    });
    mockUseTableQuery.mockReturnValue({
      defaultPage: 1,
      defaultPageSize: 10,
      page: 2,
      setPage: mockSetPage,
      pageSize: 20,
      setPageSize: mockSetPageSize,
      search: "abc",
      setSearch: mockSetSearch,
      filters: { status: "active" },
      setFilters: mockSetFilters,
      sortBy: "-id",
      action: "bulk",
      setAction: mockSetAction,
      selectedRowKeys: ["1"],
      setSelectedRowKeys: vi.fn(),
      onTableChange: vi.fn(),
      resetTable: mockResetTable,
    });
    mockUseTableColumns.mockReturnValue([]);
    mockGetConfigurationModel.mockReturnValue({
      name: "User",
      permissions: [EModelPermission.Add, EModelPermission.Export],
      actions: [{ name: "bulk", description: "Bulk action" }],
      actions_on_top: true,
      actions_on_bottom: true,
      fields: [],
      search_fields: ["name"],
      preserve_filters: true,
    });
  });

  afterEach(() => cleanup());

  it("renders actions and executes filter/change/delete callbacks", () => {
    render(
      <ConfigurationContext.Provider
        value={
          {
            configuration: {
              site_name: "Admin",
              username_field: "username",
              models: [],
              dashboard_widgets: [],
            },
          } as any
        }
      >
        <List />
      </ConfigurationContext.Provider>,
    );

    expect(screen.getAllByTestId("option-bulk").length).toBeGreaterThan(0);
    fireEvent.click(
      screen.getAllByRole("button", { name: "choose-action" })[0],
    );
    expect(mockSetAction).toHaveBeenCalledWith("bulk");

    fireEvent.click(screen.getByRole("button", { name: "Search" }));
    expect(mockSetSearch).toHaveBeenCalledWith("term");

    fireEvent.click(screen.getByRole("button", { name: /Add/i }));
    expect(mockNavigate).toHaveBeenCalledWith("/add/user");

    fireEvent.click(screen.getAllByRole("button", { name: "Apply" })[0]);
    expect(mockMutateAction).toHaveBeenCalledWith({ ids: ["1"] });

    const applyFilter = mockUseTableColumns.mock.calls[0][3] as (
      field: string,
      value: unknown,
    ) => void;
    const resetFilter = mockUseTableColumns.mock.calls[0][4] as (
      field: string,
    ) => void;
    const onDeleteItem = mockUseTableColumns.mock.calls[0][5] as (record: {
      id: string;
    }) => void;
    const onChangeItem = mockUseTableColumns.mock.calls[0][6] as (record: {
      id: string;
    }) => void;

    applyFilter("name", "alice");
    expect(mockSetFilters).toHaveBeenCalledWith({
      status: "active",
      name: "alice",
    });
    expect(mockSetPage).toHaveBeenCalledWith(1);
    expect(mockSetPageSize).toHaveBeenCalledWith(10);

    resetFilter("status");
    expect(mockSetFilters).toHaveBeenCalledWith({});

    onDeleteItem({ id: "42" });
    expect(mockMutateDelete).toHaveBeenCalledWith("42");

    onChangeItem({ id: "99" });
    expect(mockNavigate).toHaveBeenCalledWith("/change/user/99");
  });

  it("handles mutation callbacks and no-model branch", () => {
    const { rerender } = render(
      <ConfigurationContext.Provider
        value={
          {
            configuration: {
              site_name: "Admin",
              username_field: "username",
              models: [],
              dashboard_widgets: [],
            },
          } as any
        }
      >
        <List />
      </ConfigurationContext.Provider>,
    );

    const deleteMutation = mockUseMutation.mock.calls[0][0] as {
      onSuccess: () => void;
      onError: (error: Error) => void;
    };
    const actionMutation = mockUseMutation.mock.calls[1][0] as {
      onSuccess: () => void;
      onError: () => void;
    };

    deleteMutation.onSuccess();
    expect(mockResetTable).toHaveBeenCalledWith(true);
    expect(mockRefetch).toHaveBeenCalled();
    expect(mockMessageSuccess).toHaveBeenCalledWith("Successfully deleted");

    deleteMutation.onError(new Error("delete failed"));
    expect(mockHandleError).toHaveBeenCalledWith(expect.any(Error));

    actionMutation.onSuccess();
    expect(mockMessageSuccess).toHaveBeenCalledWith("Successfully applied");

    actionMutation.onError();
    expect(mockMessageError).toHaveBeenCalledWith("Server error");

    mockGetConfigurationModel.mockReturnValue(undefined);
    rerender(
      <ConfigurationContext.Provider
        value={
          {
            configuration: {
              site_name: "Admin",
              username_field: "username",
              models: [],
              dashboard_widgets: [],
            },
          } as any
        }
      >
        <List />
      </ConfigurationContext.Provider>,
    );
    expect(screen.getByText("No permissions for model")).toBeTruthy();
  });
});
