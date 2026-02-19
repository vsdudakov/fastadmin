import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import type React from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { EModelPermission } from "@/interfaces/configuration";
import { AsyncSelect } from "./index";

const {
  mockUseQuery,
  mockUseMutation,
  mockMutateAdd,
  mockMutateChange,
  mockGetConfigurationModel,
  mockHandleError,
  mockMessageSuccess,
  formAdd,
  formChange,
} = vi.hoisted(() => ({
  mockUseQuery: vi.fn(),
  mockUseMutation: vi.fn(),
  mockMutateAdd: vi.fn(),
  mockMutateChange: vi.fn(),
  mockGetConfigurationModel: vi.fn(),
  mockHandleError: vi.fn(),
  mockMessageSuccess: vi.fn(),
  formAdd: { resetFields: vi.fn() },
  formChange: { resetFields: vi.fn() },
}));

vi.mock("@tanstack/react-query", () => ({
  useQuery: (options: unknown) => mockUseQuery(options),
  useMutation: (options: unknown) => mockUseMutation(options),
}));

vi.mock("lodash.debounce", () => ({
  default: (fn: (...args: any[]) => any) => fn,
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
    useForm: vi
      .fn()
      .mockReturnValueOnce([formAdd])
      .mockReturnValueOnce([formChange])
      .mockReturnValue([formAdd]),
  },
  Space: Object.assign(
    ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
    {
      Compact: ({ children }: { children: React.ReactNode }) => (
        <div>{children}</div>
      ),
    },
  ),
  Tooltip: ({ children }: { children: React.ReactNode }) => (
    <div>{children}</div>
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
  Select: ({ onChange, onSearch, options, mode }: any) => (
    <div>
      <button type="button" onClick={() => onSearch?.("term")}>
        trigger-search
      </button>
      <button type="button" onClick={() => onChange?.("3")}>
        trigger-select
      </button>
      <button type="button" onClick={() => onChange?.(undefined)}>
        trigger-select-empty
      </button>
      {mode === "multiple" && (
        <button type="button" onClick={() => onChange?.(["1", "2"])}>
          trigger-select-multi
        </button>
      )}
      <div data-testid="options-count">{(options || []).length}</div>
    </div>
  ),
  Modal: ({
    open,
    title,
    children,
  }: {
    open: boolean;
    title: React.ReactNode;
    children: React.ReactNode;
  }) => (
    <div>
      <div>
        {String(title).includes("Change") ? "change" : "add"}-open:
        {String(open)}
      </div>
      {open ? children : null}
    </div>
  ),
  Row: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Col: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Divider: () => <hr />,
  Empty: ({ description }: { description: string }) => <div>{description}</div>,
  message: {
    success: (...args: unknown[]) => mockMessageSuccess(...args),
    error: vi.fn(),
  },
}));

vi.mock("@/components/form-container", () => ({
  FormContainer: ({
    onFinish,
    mode,
    children,
  }: {
    onFinish?: (v: any) => void;
    mode: string;
    children: React.ReactNode;
  }) => (
    <div>
      <button type="button" onClick={() => onFinish?.({ from: mode })}>
        trigger-submit-{mode}
      </button>
      {children}
    </div>
  ),
}));

vi.mock("@/helpers/configuration", () => ({
  getConfigurationModel: (...args: unknown[]) =>
    mockGetConfigurationModel(...args),
}));

vi.mock("@/helpers/title", () => ({
  getTitleFromModel: () => "Model",
}));

vi.mock("@/helpers/forms", () => ({
  handleError: (...args: unknown[]) => mockHandleError(...args),
}));

vi.mock("@/helpers/transform", () => ({
  transformDataFromServer: (v: unknown) => v,
}));

describe("AsyncSelect", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseQuery.mockImplementation((options: any) => {
      if ((options?.queryKey?.[0] || "").includes("/list/")) {
        return {
          data: {
            results: [
              { id: 1, name: "One" },
              { id: 2, title: "Two" },
            ],
          },
          isLoading: false,
          refetch: vi.fn(),
        };
      }
      return {
        data: { id: 1, name: "One" },
        isLoading: false,
      };
    });
    let mutationCall = 0;
    mockUseMutation.mockImplementation(() => {
      const idx = mutationCall % 2;
      mutationCall += 1;
      if (idx === 0) {
        return { mutate: mockMutateAdd, isPending: false, isError: false };
      }
      return { mutate: mockMutateChange, isPending: false, isError: false };
    });
    mockGetConfigurationModel.mockReturnValue({
      name: "test",
      permissions: [EModelPermission.Add, EModelPermission.Change],
      fields: [],
      actions: [],
    });
  });

  afterEach(() => {
    cleanup();
  });

  it("handles single mode select and add/change submit handlers", async () => {
    const onChange = vi.fn();
    const { container } = render(
      <AsyncSelect
        idField="id"
        labelFields={["name", "title"]}
        parentModel="test"
        value={1}
        onChange={onChange}
      />,
    );

    const firstQuery = mockUseQuery.mock.calls[0][0] as any;
    expect(firstQuery.queryKey[1]).toContain("offset=0");
    expect(screen.getByTestId("options-count").textContent).toBe("2");

    fireEvent.click(
      screen.getByRole("button", { name: "trigger-select-empty" }),
    );
    expect(onChange).toHaveBeenCalledWith(null);
    fireEvent.click(screen.getByRole("button", { name: "trigger-select" }));
    expect(onChange).toHaveBeenCalledWith("3");

    fireEvent.click(screen.getByRole("button", { name: "trigger-search" }));
    await waitFor(() => {
      const calls = mockUseQuery.mock.calls.map((call) => call[0] as any);
      const listCalls = calls.filter(
        (call) => call.queryKey[0] === "/list/test",
      );
      const last = listCalls[listCalls.length - 1];
      expect(last).toBeTruthy();
      expect(String(last.queryKey[1])).toContain("search=term");
    });

    const buttons = container.querySelectorAll("button");
    fireEvent.click(buttons[0]);
    fireEvent.click(
      screen.getByRole("button", { name: "trigger-submit-inline-add" }),
    );
    expect(mockMutateAdd).toHaveBeenCalledWith({ from: "inline-add" });

    fireEvent.click(buttons[1]);
    fireEvent.click(
      screen.getByRole("button", { name: "trigger-submit-inline-change" }),
    );
    expect(mockMutateChange).toHaveBeenCalledWith({ from: "inline-change" });
    expect(formAdd.resetFields).toHaveBeenCalled();
  });

  it("handles multiple mode onChange branch", () => {
    const onChange = vi.fn();
    render(
      <AsyncSelect
        idField="id"
        labelFields={["name"]}
        parentModel="test"
        {...({ mode: "multiple" } as any)}
        value={[1]}
        onChange={onChange}
      />,
    );

    fireEvent.click(
      screen.getByRole("button", { name: "trigger-select-multi" }),
    );
    expect(onChange).toHaveBeenCalledWith(["1", "2"]);
  });

  it("covers mutation callbacks and permission fallbacks", () => {
    const { rerender } = render(
      <AsyncSelect
        idField="id"
        labelFields={["name"]}
        parentModel="test"
        value={1}
      />,
    );
    const addMutation = mockUseMutation.mock.calls[0][0] as any;
    const changeMutation = mockUseMutation.mock.calls[1][0] as any;

    addMutation.onSuccess();
    changeMutation.onSuccess();
    expect(mockMessageSuccess).toHaveBeenCalledWith("Succesfully added");
    expect(mockMessageSuccess).toHaveBeenCalledWith("Succesfully changed");

    addMutation.onError(new Error("add"));
    changeMutation.onError(new Error("change"));
    expect(mockHandleError).toHaveBeenCalledTimes(2);
    expect(mockHandleError.mock.calls[0][0]).toBeInstanceOf(Error);
    expect(mockHandleError.mock.calls[0][1]).toBeTruthy();
    expect(mockHandleError.mock.calls[1][0]).toBeInstanceOf(Error);
    expect(mockHandleError.mock.calls[1][1]).toBeTruthy();

    mockGetConfigurationModel.mockReturnValue({
      name: "test",
      permissions: [],
      fields: [],
      actions: [],
    });
    rerender(
      <AsyncSelect
        idField="id"
        labelFields={["name"]}
        parentModel="test"
        value={1}
      />,
    );
    const btns = screen.getAllByRole("button");
    fireEvent.click(btns[0]);
    fireEvent.click(btns[1]);
    expect(
      screen.getAllByText("No permissions for model").length,
    ).toBeGreaterThan(0);
  });
});
