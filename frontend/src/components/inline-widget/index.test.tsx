import {
  act,
  cleanup,
  fireEvent,
  render,
  screen,
} from "@testing-library/react";
import type React from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { InlineWidget } from "@/components/inline-widget";
import { EModelPermission } from "@/interfaces/configuration";
import { ConfigurationContext } from "@/providers/ConfigurationProvider";

const {
  mockUseQuery,
  mockUseMutation,
  mockUseTableQuery,
  mockUseTableColumns,
  mockMutateAction,
  mockMutateAdd,
  mockMutateChange,
  mockMutateDelete,
  mockSetAction,
  mockSetFilters,
  mockSetPage,
  mockSetPageSize,
  mockResetTable,
  mockRefetch,
  mockMessageSuccess,
  mockMessageError,
  mockHandleError,
  mockPatchFetcher,
  mockDeleteFetcher,
  mockPostFetcher,
} = vi.hoisted(() => ({
  mockUseQuery: vi.fn(),
  mockUseMutation: vi.fn(),
  mockUseTableQuery: vi.fn(),
  mockUseTableColumns: vi.fn(),
  mockMutateAction: vi.fn(),
  mockMutateAdd: vi.fn(),
  mockMutateChange: vi.fn(),
  mockMutateDelete: vi.fn(),
  mockSetAction: vi.fn(),
  mockSetFilters: vi.fn(),
  mockSetPage: vi.fn(),
  mockSetPageSize: vi.fn(),
  mockResetTable: vi.fn(),
  mockRefetch: vi.fn(),
  mockMessageSuccess: vi.fn(),
  mockMessageError: vi.fn(),
  mockHandleError: vi.fn(),
  mockPatchFetcher: vi.fn(),
  mockDeleteFetcher: vi.fn(),
  mockPostFetcher: vi.fn(),
}));

vi.mock("@tanstack/react-query", () => ({
  useQuery: (options: any) => mockUseQuery(options),
  useMutation: (options: any) => mockUseMutation(options),
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
  Form: {
    useForm: () => [{ resetFields: vi.fn(), setFieldValue: vi.fn() }],
  },
  message: {
    success: (...args: unknown[]) => mockMessageSuccess(...args),
    error: (...args: unknown[]) => mockMessageError(...args),
  },
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
  Modal: ({
    open,
    title,
    children,
  }: {
    open: boolean;
    title?: React.ReactNode;
    children: React.ReactNode;
  }) =>
    open ? (
      <div>
        <div>{title}</div>
        {children}
      </div>
    ) : null,
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
          trigger-select
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
      }) => <div data-testid={`opt-${value}`}>{children}</div>,
    },
  ),
  Input: {
    Search: ({ onSearch }: { onSearch?: (v: string) => void }) => (
      <button type="button" onClick={() => onSearch?.("q")}>
        trigger-search
      </button>
    ),
  },
  Row: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Col: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Space: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Divider: () => <hr />,
  Empty: ({ description }: { description: string }) => <div>{description}</div>,
}));

vi.mock("@/components/table-or-cards", () => ({
  TableOrCards: ({
    title,
    footer,
  }: {
    title?: () => React.ReactNode;
    footer?: () => React.ReactNode;
  }) => (
    <div>
      <div data-testid="table-header">{title?.()}</div>
      <div data-testid="table-footer">{footer?.()}</div>
    </div>
  ),
}));

vi.mock("@/components/export-btn", () => ({
  ExportBtn: () => <div>export-btn</div>,
}));

vi.mock("@/components/form-container", () => ({
  FormContainer: ({
    children,
    onFinish,
    mode,
  }: {
    children: React.ReactNode;
    onFinish?: (payload: any) => void;
    mode?: string;
  }) => (
    <div>
      <button
        type="button"
        onClick={() => onFinish?.({ name: mode || "payload" })}
      >
        trigger-submit-{mode}
      </button>
      {children}
    </div>
  ),
}));

vi.mock("@/helpers/title", () => ({
  getTitleFromModel: () => "Users",
}));

vi.mock("@/helpers/forms", () => ({
  handleError: (...args: unknown[]) => mockHandleError(...args),
}));

vi.mock("@/helpers/transform", () => ({
  transformDataFromServer: (v: unknown) => v,
  transformFiltersToServer: () => ({}),
}));

vi.mock("@/fetchers/fetchers", () => ({
  getFetcher: vi.fn(),
  postFetcher: (...args: unknown[]) => mockPostFetcher(...args),
  patchFetcher: (...args: unknown[]) => mockPatchFetcher(...args),
  deleteFetcher: (...args: unknown[]) => mockDeleteFetcher(...args),
}));

vi.mock("@/hooks/useTableColumns", () => ({
  useTableColumns: (...args: unknown[]) => mockUseTableColumns(...args),
}));

vi.mock("@/hooks/useTableQuery", () => ({
  useTableQuery: (...args: unknown[]) => mockUseTableQuery(...args),
}));

describe("InlineWidget", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseQuery.mockImplementation((options: any) => {
      if ((options?.queryKey?.[0] || "").includes("/list/")) {
        return {
          data: { results: [{ id: "2" }], total: 1 },
          isLoading: false,
          refetch: mockRefetch,
        };
      }
      if ((options?.queryKey?.[0] || "").includes("/retrieve/")) {
        return {
          data: { id: "2", name: "Item 2" },
          isLoading: false,
        };
      }
      return { data: undefined, isLoading: false };
    });
    let mutationHookCall = 0;
    mockUseMutation.mockImplementation(() => {
      const index = mutationHookCall % 4;
      mutationHookCall += 1;
      if (index === 0) {
        return {
          mutate: mockMutateAdd,
          isPending: false,
          isError: false,
        };
      }
      if (index === 1) {
        return {
          mutate: mockMutateChange,
          isPending: false,
          isError: false,
        };
      }
      if (index === 2) {
        return {
          mutate: mockMutateDelete,
        };
      }
      return {
        mutate: mockMutateAction,
        isPending: false,
      };
    });
    mockUseTableQuery.mockReturnValue({
      defaultPage: 1,
      defaultPageSize: 10,
      page: 2,
      setPage: mockSetPage,
      pageSize: 5,
      setPageSize: mockSetPageSize,
      search: "abc",
      setSearch: vi.fn(),
      filters: { status: "active" },
      setFilters: mockSetFilters,
      sortBy: "-id",
      action: "bulk",
      setAction: mockSetAction,
      selectedRowKeys: ["1"],
      setSelectedRowKeys: vi.fn(),
      resetTable: mockResetTable,
      onTableChange: vi.fn(),
    });
    mockUseTableColumns.mockReturnValue([]);
  });

  afterEach(() => {
    cleanup();
  });

  it("renders top and bottom actions and applies selected action", () => {
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
        <InlineWidget
          parentId="parent-1"
          modelConfiguration={{
            name: "InlineModel",
            fields: [],
            permissions: [EModelPermission.Add, EModelPermission.Export],
            actions: [{ name: "bulk", description: "Bulk Action" }],
            actions_on_top: true,
            actions_on_bottom: true,
            fk_name: "parent_id",
          }}
        />
      </ConfigurationContext.Provider>,
    );

    fireEvent.click(screen.getByRole("button", { name: "Change" }));

    expect(screen.getAllByTestId("opt-bulk").length).toBeGreaterThan(0);
    expect(
      screen.getAllByRole("button", { name: "Apply" }).length,
    ).toBeGreaterThan(0);
    fireEvent.click(screen.getAllByRole("button", { name: "Apply" })[0]);
    expect(mockMutateAction).toHaveBeenCalledWith({ ids: ["1"] });
  });

  it("applies filter callbacks and add/change submissions", () => {
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
        <InlineWidget
          parentId="parent-1"
          modelConfiguration={{
            name: "InlineModel",
            fields: [],
            permissions: [EModelPermission.Add, EModelPermission.Change],
            actions: [],
            fk_name: "parent_id",
          }}
        />
      </ConfigurationContext.Provider>,
    );

    const getFilterValue = mockUseTableColumns.mock.calls[0][2] as (
      field: string,
    ) => unknown;
    const onApplyFilter = mockUseTableColumns.mock.calls[0][3] as (
      field: string,
      value: unknown,
    ) => void;
    const onResetFilter = mockUseTableColumns.mock.calls[0][4] as (
      field: string,
    ) => void;
    const onDeleteItem = mockUseTableColumns.mock.calls[0][5] as (record: {
      id: string;
    }) => void;
    const onChangeItem = mockUseTableColumns.mock.calls[0][6] as (record: {
      id: string;
    }) => void;

    expect(getFilterValue("status")).toBe("active");
    onApplyFilter("name", "john");
    expect(mockSetFilters).toHaveBeenCalledWith({
      status: "active",
      name: "john",
    });
    expect(mockSetPage).toHaveBeenCalledWith(1);
    expect(mockSetPageSize).toHaveBeenCalledWith(10);

    onResetFilter("status");
    expect(mockSetFilters).toHaveBeenCalledWith({});

    onDeleteItem({ id: "42" });
    expect(mockMutateDelete).toHaveBeenCalledWith("42");

    fireEvent.click(screen.getByRole("button", { name: "Change" }));
    fireEvent.click(screen.getByRole("button", { name: /Add/ }));
    fireEvent.click(
      screen.getByRole("button", { name: "trigger-submit-inline-add" }),
    );
    expect(mockMutateAdd).toHaveBeenCalledWith({ name: "inline-add" });

    act(() => {
      onChangeItem({ id: "2" });
    });
    fireEvent.click(
      screen.getByRole("button", { name: "trigger-submit-inline-change" }),
    );
    expect(mockMutateChange).toHaveBeenCalledWith({ name: "inline-change" });
  });

  it("handles delete/action mutation success and error callbacks", () => {
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
        <InlineWidget
          parentId="parent-1"
          modelConfiguration={{
            name: "InlineModel",
            fields: [],
            permissions: [EModelPermission.Add, EModelPermission.Change],
            actions: [{ name: "bulk", description: "Bulk Action" }],
            fk_name: "parent_id",
          }}
        />
      </ConfigurationContext.Provider>,
    );

    const deleteMutation = mockUseMutation.mock.calls[2][0] as {
      onSuccess: () => void;
      onError: (error: Error) => void;
    };
    const actionMutation = mockUseMutation.mock.calls[3][0] as {
      onSuccess: () => void;
      onError: () => void;
    };

    deleteMutation.onSuccess();
    expect(mockResetTable).toHaveBeenCalled();
    expect(mockRefetch).toHaveBeenCalled();
    expect(mockMessageSuccess).toHaveBeenCalledWith("Successfully deleted");

    deleteMutation.onError(new Error("delete failed"));
    expect(mockHandleError).toHaveBeenCalledWith(expect.any(Error));

    actionMutation.onSuccess();
    expect(mockMessageSuccess).toHaveBeenCalledWith("Successfully applied");

    actionMutation.onError();
    expect(mockMessageError).toHaveBeenCalledWith("Server error");
  });

  it("calls mutation functions and handles add/change callbacks", async () => {
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
        <InlineWidget
          parentId="parent-1"
          modelConfiguration={{
            name: "InlineModel",
            fields: [],
            permissions: [EModelPermission.Change],
            actions: [{ name: "bulk", description: "Bulk Action" }],
            fk_name: "parent_id",
          }}
        />
      </ConfigurationContext.Provider>,
    );

    const addMutation = mockUseMutation.mock.calls[0][0] as {
      mutationFn: (payload: unknown) => Promise<unknown> | unknown;
      onSuccess: () => void;
      onError: (error: Error) => void;
    };
    const changeMutation = mockUseMutation.mock.calls[1][0] as {
      mutationFn: (payload: unknown) => Promise<unknown> | unknown;
      onSuccess: () => void;
      onError: (error: Error) => void;
    };
    const deleteMutation = mockUseMutation.mock.calls[2][0] as {
      mutationFn: (id: string) => Promise<unknown> | unknown;
    };
    const actionMutation = mockUseMutation.mock.calls[3][0] as {
      mutationFn: (payload: unknown) => Promise<unknown> | unknown;
    };

    await addMutation.mutationFn({ title: "add" });
    expect(mockPostFetcher).toHaveBeenCalledWith("/add/InlineModel", {
      title: "add",
    });
    addMutation.onSuccess();
    expect(mockMessageSuccess).toHaveBeenCalledWith("Succesfully added");
    addMutation.onError(new Error("add failed"));
    expect(mockHandleError).toHaveBeenCalledWith(
      expect.any(Error),
      expect.any(Object),
    );

    await changeMutation.mutationFn({ title: "new" });
    expect(mockPatchFetcher).toHaveBeenCalledWith(
      "/change/InlineModel/undefined",
      { title: "new" },
    );
    changeMutation.onError(new Error("change failed"));
    expect(mockHandleError).toHaveBeenCalledWith(
      expect.any(Error),
      expect.any(Object),
    );
    changeMutation.onSuccess();
    expect(mockMessageSuccess).toHaveBeenCalledWith("Succesfully changed");

    await deleteMutation.mutationFn("42");
    expect(mockDeleteFetcher).toHaveBeenCalledWith("/delete/InlineModel/42");

    await actionMutation.mutationFn({ ids: ["1"] });
    expect(mockPostFetcher).toHaveBeenCalledWith("/action/InlineModel/bulk", {
      ids: ["1"],
    });
  });
});
