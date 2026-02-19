import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import type React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { PasswordInput } from "@/components/password-input";

const {
  mockUseMutation,
  mockMutate,
  mockPatchFetcher,
  mockHandleError,
  mockMessageSuccess,
  formMock,
} = vi.hoisted(() => ({
  mockUseMutation: vi.fn(),
  mockMutate: vi.fn(),
  mockPatchFetcher: vi.fn(),
  mockHandleError: vi.fn(),
  mockMessageSuccess: vi.fn(),
  formMock: {
    resetFields: vi.fn(),
  },
}));

vi.mock("@tanstack/react-query", () => ({
  useMutation: (options: unknown) => mockUseMutation(options),
}));

vi.mock("@/fetchers/fetchers", () => ({
  patchFetcher: (...args: unknown[]) => mockPatchFetcher(...args),
}));

vi.mock("@/helpers/forms", () => ({
  handleError: (...args: unknown[]) => mockHandleError(...args),
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
  message: {
    success: (...args: unknown[]) => mockMessageSuccess(...args),
  },
  Form: Object.assign(
    ({
      children,
      onFinish,
    }: {
      children: React.ReactNode;
      onFinish?: (payload: unknown) => void;
    }) => (
      <div>
        <button type="button" onClick={() => onFinish?.({ password: "p" })}>
          trigger-finish
        </button>
        {children}
      </div>
    ),
    {
      useForm: () => [formMock],
      Item: ({ children }: { children: React.ReactNode }) => (
        <div>{children}</div>
      ),
    },
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
  Divider: () => <hr />,
  Input: {
    Password: ({ disabled }: { disabled?: boolean }) => (
      <input data-testid="password-input" disabled={disabled} />
    ),
  },
  Modal: ({
    open,
    onCancel,
    children,
  }: {
    open: boolean;
    onCancel: () => void;
    children: React.ReactNode;
  }) => (
    <div>
      <div data-testid="modal-open">{String(open)}</div>
      <button type="button" onClick={onCancel}>
        trigger-cancel
      </button>
      {open ? children : null}
    </div>
  ),
}));

describe("PasswordInput", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("renders plain password field without parentId", () => {
    mockUseMutation.mockReturnValue({
      mutate: mockMutate,
      isPending: false,
    });

    render(<PasswordInput />);
    expect(screen.getByTestId("password-input")).toBeTruthy();
    expect(screen.queryByText("trigger-cancel")).toBeNull();
  });

  it("opens modal, submits and closes with parentId", () => {
    mockUseMutation.mockReturnValue({
      mutate: mockMutate,
      isPending: false,
    });

    render(<PasswordInput parentId="user-1" />);

    fireEvent.click(screen.getByRole("button", { name: /edit/i }));
    expect(screen.getByTestId("modal-open").textContent).toBe("true");
    expect(formMock.resetFields).toHaveBeenCalled();

    fireEvent.click(screen.getByText("trigger-finish"));
    expect(mockMutate).toHaveBeenCalledWith({ password: "p" });

    fireEvent.click(screen.getByText("trigger-cancel"));
    expect(screen.getByTestId("modal-open").textContent).toBe("false");
  });

  it("uses mutation callbacks for success and error", async () => {
    let mutationOptions: any;
    mockUseMutation.mockImplementation((options: any) => {
      mutationOptions = options;
      return { mutate: mockMutate, isPending: false };
    });

    render(<PasswordInput parentId="user-1" />);

    await mutationOptions.mutationFn({ password: "x" });
    expect(mockPatchFetcher).toHaveBeenCalledWith("/change-password/user-1", {
      password: "x",
    });

    mutationOptions.onSuccess();
    expect(mockMessageSuccess).toHaveBeenCalledWith("Succesfully changed");
    expect(formMock.resetFields).toHaveBeenCalled();

    const error = new Error("fail");
    mutationOptions.onError(error);
    expect(mockHandleError).toHaveBeenCalled();
  });
});
