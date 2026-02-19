import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import type React from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { Change } from "@/containers/change";
import { EModelPermission } from "@/interfaces/configuration";
import { ConfigurationContext } from "@/providers/ConfigurationProvider";

const {
  mockUseQuery,
  mockUseMutation,
  mockGetConfigurationModel,
  mockForm,
  mockUseIsMobile,
  mockNavigate,
  mockInvalidateQueries,
  mockMessageSuccess,
  mockMessageError,
  mockHandleError,
  mockTransformDataToServer,
  mockDeleteFetcher,
  mockPostFetcher,
  mockPatchFetcher,
} = vi.hoisted(() => ({
  mockUseQuery: vi.fn(),
  mockUseMutation: vi.fn(),
  mockGetConfigurationModel: vi.fn(),
  mockForm: {
    setFieldValue: vi.fn(),
    getFieldValue: vi.fn(),
    submit: vi.fn(),
  },
  mockUseIsMobile: vi.fn(),
  mockNavigate: vi.fn(),
  mockInvalidateQueries: vi.fn(),
  mockMessageSuccess: vi.fn(),
  mockMessageError: vi.fn(),
  mockHandleError: vi.fn(),
  mockTransformDataToServer: vi.fn(),
  mockDeleteFetcher: vi.fn(),
  mockPostFetcher: vi.fn(),
  mockPatchFetcher: vi.fn(),
}));

vi.mock("@tanstack/react-query", () => ({
  useQuery: (options: unknown) => mockUseQuery(options),
  useMutation: (options: unknown) => mockUseMutation(options),
  useQueryClient: () => ({
    invalidateQueries: (...args: unknown[]) => mockInvalidateQueries(...args),
  }),
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
    useParams: () => ({ model: "user", id: "1" }),
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
  Form: {
    useForm: () => [mockForm],
  },
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
  Empty: ({ description }: { description: string }) => <div>{description}</div>,
  Row: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Col: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Space: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Popconfirm: ({
    children,
    onConfirm,
  }: {
    children: React.ReactNode;
    onConfirm?: () => void;
  }) => (
    <div>
      <button type="button" onClick={onConfirm}>
        confirm-delete
      </button>
      {children}
    </div>
  ),
  Button: ({
    children,
    onClick,
  }: {
    children: React.ReactNode;
    onClick?: () => void;
  }) => (
    <button type="button" onClick={onClick}>
      {children}
    </button>
  ),
}));

vi.mock("@/components/crud-container", () => ({
  CrudContainer: ({ children }: { children: React.ReactNode }) => (
    <div>{children}</div>
  ),
}));

vi.mock("@/components/form-container", () => ({
  FormContainer: ({
    children,
    onFinish,
  }: {
    children: React.ReactNode;
    onFinish?: (payload: unknown) => void;
  }) => (
    <div>
      <button type="button" onClick={() => onFinish?.({ name: "Alice" })}>
        trigger-form-finish
      </button>
      {children}
    </div>
  ),
}));

vi.mock("@/helpers/configuration", () => ({
  getConfigurationModel: (...args: unknown[]) =>
    mockGetConfigurationModel(...args),
}));

vi.mock("@/helpers/forms", () => ({
  handleError: (...args: unknown[]) => mockHandleError(...args),
}));

vi.mock("@/helpers/title", () => ({
  getTitleFromModel: () => "User",
}));

vi.mock("@/helpers/transform", () => ({
  transformDataFromServer: (data: unknown) => data,
  transformDataToServer: (...args: unknown[]) =>
    mockTransformDataToServer(...args),
}));

vi.mock("@/fetchers/fetchers", () => ({
  getFetcher: vi.fn(),
  postFetcher: (...args: unknown[]) => mockPostFetcher(...args),
  patchFetcher: (...args: unknown[]) => mockPatchFetcher(...args),
  deleteFetcher: (...args: unknown[]) => mockDeleteFetcher(...args),
}));

vi.mock("@/hooks/useIsMobile", () => ({
  useIsMobile: () => mockUseIsMobile(),
}));

describe("Change container", () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    vi.clearAllMocks();
    mockUseIsMobile.mockReturnValue(false);
    mockUseQuery.mockReturnValue({
      data: { id: 1, name: "Alice" },
      isLoading: false,
    });
    mockUseMutation.mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
      isError: false,
    });
    mockForm.getFieldValue.mockReturnValue(undefined);
    mockTransformDataToServer.mockImplementation((data: unknown) => ({
      ...(data as object),
      transformed: true,
    }));
  });

  it("sets next and save_as_new on save as new", () => {
    mockGetConfigurationModel.mockReturnValue({
      name: "User",
      permissions: [EModelPermission.Change],
      actions: [],
      fields: [],
      save_as: true,
      save_as_continue: false,
    });

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
        <Change />
      </ConfigurationContext.Provider>,
    );

    fireEvent.click(screen.getByRole("button", { name: /Save as new/i }));

    expect(mockForm.setFieldValue).toHaveBeenCalledWith("next", "/add/user");
    expect(mockForm.setFieldValue).toHaveBeenCalledWith("save_as_new", true);
    expect(mockForm.submit).toHaveBeenCalled();
  });

  it("sets next to list on save when save_as_continue is disabled", () => {
    mockGetConfigurationModel.mockReturnValue({
      name: "User",
      permissions: [EModelPermission.Change],
      actions: [],
      fields: [],
      save_as: false,
      save_as_continue: false,
    });

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
        <Change />
      </ConfigurationContext.Provider>,
    );

    const saveButtons = screen.getAllByRole("button", { name: /Save$/i });
    const saveButton = saveButtons[saveButtons.length - 1];
    expect(saveButton).toBeTruthy();
    if (saveButton) {
      fireEvent.click(saveButton);
    }

    expect(mockForm.setFieldValue).toHaveBeenCalledWith("next", "/list/user");
    expect(mockForm.submit).toHaveBeenCalled();
  });

  it("does not set next on save when save_as_continue is enabled", () => {
    mockGetConfigurationModel.mockReturnValue({
      name: "User",
      permissions: [EModelPermission.Change],
      actions: [],
      fields: [],
      save_as: false,
      save_as_continue: true,
    });

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
        <Change />
      </ConfigurationContext.Provider>,
    );

    const saveButtons = screen.getAllByRole("button", { name: /Save$/i });
    const saveButton = saveButtons[saveButtons.length - 1];
    expect(saveButton).toBeTruthy();
    if (saveButton) {
      fireEvent.click(saveButton);
    }

    expect(mockForm.setFieldValue).not.toHaveBeenCalledWith(
      "next",
      "/list/user",
    );
    expect(mockForm.submit).toHaveBeenCalled();
  });

  it("submits form on save and continue editing", () => {
    mockGetConfigurationModel.mockReturnValue({
      name: "User",
      permissions: [EModelPermission.Change],
      actions: [],
      fields: [],
      save_as: false,
      save_as_continue: false,
    });

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
        <Change />
      </ConfigurationContext.Provider>,
    );

    fireEvent.click(
      screen.getByRole("button", { name: /Save and continue editing/i }),
    );
    expect(mockForm.submit).toHaveBeenCalled();
  });

  it("covers onFinish add/change branches and mutation callbacks", async () => {
    const mutateAdd = vi.fn();
    const mutateChange = vi.fn();
    const mutateDelete = vi.fn();
    let mutationCall = 0;
    mockUseMutation.mockImplementation(() => {
      const idx = mutationCall % 3;
      mutationCall += 1;
      if (idx === 0) {
        return { mutate: mutateAdd, isPending: false, isError: false };
      }
      if (idx === 1) {
        return { mutate: mutateChange, isPending: false, isError: false };
      }
      return { mutate: mutateDelete };
    });
    mockGetConfigurationModel.mockReturnValue({
      name: "User",
      permissions: [EModelPermission.Change, EModelPermission.Delete],
      actions: [],
      fields: [],
      save_as: true,
      save_as_continue: false,
    });

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
        <Change />
      </ConfigurationContext.Provider>,
    );

    fireEvent.click(
      screen.getByRole("button", { name: "trigger-form-finish" }),
    );
    expect(mockTransformDataToServer).toHaveBeenCalledWith({ name: "Alice" });
    expect(mutateChange).toHaveBeenCalledWith({
      name: "Alice",
      transformed: true,
    });

    mockForm.getFieldValue.mockImplementation((field: string) =>
      field === "save_as_new" ? true : undefined,
    );
    fireEvent.click(
      screen.getByRole("button", { name: "trigger-form-finish" }),
    );
    expect(mutateAdd).toHaveBeenCalledWith({
      name: "Alice",
      transformed: true,
    });

    const addOptions = mockUseMutation.mock.calls[0][0] as any;
    const changeOptions = mockUseMutation.mock.calls[1][0] as any;
    const deleteOptions = mockUseMutation.mock.calls[2][0] as any;

    await addOptions.mutationFn({ x: 1 });
    expect(mockPostFetcher).toHaveBeenCalledWith("/add/user", { x: 1 });
    addOptions.onSuccess();
    expect(mockMessageSuccess).toHaveBeenCalledWith("Succesfully added");
    expect(mockInvalidateQueries).toHaveBeenCalledWith(["/list/user"]);
    addOptions.onError(new Error("add error"));

    await changeOptions.mutationFn({ y: 1 });
    expect(mockPatchFetcher).toHaveBeenCalledWith("/change/user/1", { y: 1 });
    changeOptions.onSuccess();
    expect(mockMessageSuccess).toHaveBeenCalledWith("Succesfully changed");
    expect(mockInvalidateQueries).toHaveBeenCalledWith(["/retrieve/user/1"]);
    expect(mockInvalidateQueries).toHaveBeenCalledWith(["/list/user"]);
    changeOptions.onError(new Error("change error"));
    expect(mockHandleError).toHaveBeenCalledWith(expect.any(Error), mockForm);

    await deleteOptions.mutationFn();
    expect(mockDeleteFetcher).toHaveBeenCalledWith("/delete/user/1");
    deleteOptions.onSuccess();
    expect(mockMessageSuccess).toHaveBeenCalledWith("Successfully deleted");
    expect(mockNavigate).toHaveBeenCalledWith("/list/user");
    deleteOptions.onError();
    expect(mockMessageError).toHaveBeenCalledWith("Server error");

    fireEvent.click(screen.getByRole("button", { name: "confirm-delete" }));
    expect(mutateDelete).toHaveBeenCalled();
  });
});
