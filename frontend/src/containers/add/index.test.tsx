import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import type React from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { EModelPermission } from "@/interfaces/configuration";
import { ConfigurationContext } from "@/providers/ConfigurationProvider";
import { Add } from "./index";

const {
  mockUseMutation,
  mockMutate,
  mockInvalidateQueries,
  mockNavigate,
  mockPostFetcher,
  mockTransformDataToServer,
  mockHandleError,
  mockMessageSuccess,
  formMock,
} = vi.hoisted(() => ({
  mockUseMutation: vi.fn(),
  mockMutate: vi.fn(),
  mockInvalidateQueries: vi.fn(),
  mockNavigate: vi.fn(),
  mockPostFetcher: vi.fn(),
  mockTransformDataToServer: vi.fn(),
  mockHandleError: vi.fn(),
  mockMessageSuccess: vi.fn(),
  formMock: {},
}));

vi.mock("@tanstack/react-query", () => ({
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
  Form: {
    useForm: () => [formMock],
  },
  message: {
    success: (...args: unknown[]) => mockMessageSuccess(...args),
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
  Space: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
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
  Empty: ({ description }: { description: string }) => <div>{description}</div>,
}));

vi.mock("@/components/crud-container", () => ({
  CrudContainer: ({ children }: { children: React.ReactNode }) => (
    <div>{children}</div>
  ),
}));

vi.mock("@/components/form-container", () => ({
  FormContainer: ({
    onFinish,
    children,
  }: {
    onFinish?: (payload: unknown) => void;
    children: React.ReactNode;
  }) => (
    <div>
      <button type="button" onClick={() => onFinish?.({ name: "john" })}>
        trigger-submit
      </button>
      {children}
    </div>
  ),
}));

vi.mock("@/fetchers/fetchers", () => ({
  postFetcher: (...args: unknown[]) => mockPostFetcher(...args),
}));

vi.mock("@/helpers/configuration", () => ({
  getConfigurationModel: () => ({
    name: "user",
    permissions: [EModelPermission.Add],
    actions: [],
    fields: [],
  }),
}));

vi.mock("@/helpers/forms", () => ({
  handleError: (...args: unknown[]) => mockHandleError(...args),
}));

vi.mock("@/helpers/title", () => ({
  getTitleFromModel: () => "User",
}));

vi.mock("@/helpers/transform", () => ({
  transformDataToServer: (...args: unknown[]) =>
    mockTransformDataToServer(...args),
}));

describe("Add container", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseMutation.mockReturnValue({
      mutate: mockMutate,
      isPending: false,
      isError: false,
    });
    mockTransformDataToServer.mockReturnValue({ name: "john-transformed" });
  });

  afterEach(() => {
    cleanup();
  });

  it("submits transformed payload via mutate", () => {
    render(
      <ConfigurationContext.Provider
        value={{ configuration: { models: [], dashboard_widgets: [] } } as any}
      >
        <Add />
      </ConfigurationContext.Provider>,
    );

    fireEvent.click(screen.getByRole("button", { name: "trigger-submit" }));
    expect(mockTransformDataToServer).toHaveBeenCalledWith({ name: "john" });
    expect(mockMutate).toHaveBeenCalledWith({ name: "john-transformed" });
  });

  it("handles mutation callbacks", async () => {
    render(
      <ConfigurationContext.Provider
        value={{ configuration: { models: [], dashboard_widgets: [] } } as any}
      >
        <Add />
      </ConfigurationContext.Provider>,
    );

    const mutationOptions = mockUseMutation.mock.calls[0][0] as {
      mutationFn: (payload: unknown) => Promise<unknown> | unknown;
      onSuccess: () => void;
      onError: (error: Error) => void;
    };

    await mutationOptions.mutationFn({ title: "x" });
    expect(mockPostFetcher).toHaveBeenCalledWith("/add/user", { title: "x" });

    mutationOptions.onSuccess();
    expect(mockMessageSuccess).toHaveBeenCalledWith("Succesfully added");
    expect(mockInvalidateQueries).toHaveBeenCalledWith(["/list/user"]);
    expect(mockNavigate).toHaveBeenCalledWith("/list/user");

    mutationOptions.onError(new Error("save failed"));
    expect(mockHandleError).toHaveBeenCalledWith(expect.any(Error), formMock);
  });
});
