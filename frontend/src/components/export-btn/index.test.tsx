import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import type React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { EExportFormat } from "@/interfaces/configuration";
import { ExportBtn } from "./index";

const {
  mockUseMutation,
  mockMutate,
  mockPostFetcher,
  mockFileDownload,
  mockMessageSuccess,
  mockMessageError,
  formMock,
} = vi.hoisted(() => ({
  mockUseMutation: vi.fn(),
  mockMutate: vi.fn(),
  mockPostFetcher: vi.fn(),
  mockFileDownload: vi.fn(),
  mockMessageSuccess: vi.fn(),
  mockMessageError: vi.fn(),
  formMock: {
    resetFields: vi.fn(),
    getFieldValue: vi.fn(),
  },
}));

vi.mock("@tanstack/react-query", () => ({
  useMutation: (options: unknown) => mockUseMutation(options),
}));

vi.mock("js-file-download", () => ({
  default: (...args: unknown[]) => mockFileDownload(...args),
}));

vi.mock("@/fetchers/fetchers", () => ({
  postFetcher: (...args: unknown[]) => mockPostFetcher(...args),
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
    error: (...args: unknown[]) => mockMessageError(...args),
  },
  Row: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Col: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Space: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Divider: () => <hr />,
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
        close-modal
      </button>
      {open ? children : null}
    </div>
  ),
  Form: Object.assign(
    ({
      children,
      onFinish,
    }: {
      children: React.ReactNode;
      onFinish?: (payload: unknown) => void;
    }) => (
      <div>
        <button type="button" onClick={() => onFinish?.({ limit: 10 })}>
          trigger-submit
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
  Select: Object.assign(
    ({ options }: { options?: unknown[] }) => (
      <div>{(options || []).length}</div>
    ),
    {
      Option: ({ children }: { children: React.ReactNode }) => (
        <div>{children}</div>
      ),
    },
  ),
  InputNumber: () => <input />,
}));

describe("ExportBtn", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("opens modal and submits export payload", () => {
    mockUseMutation.mockReturnValue({
      mutate: mockMutate,
      isPending: false,
    });

    render(
      <ExportBtn model="Event" search="abc" sortBy="-id" filters={{ a: 1 }} />,
    );

    fireEvent.click(screen.getByRole("button", { name: /Export/i }));
    expect(screen.getByTestId("modal-open").textContent).toBe("true");

    fireEvent.click(screen.getByRole("button", { name: "trigger-submit" }));
    expect(mockMutate).toHaveBeenCalledWith({ limit: 10 });

    fireEvent.click(screen.getByRole("button", { name: "close-modal" }));
    expect(screen.getByTestId("modal-open").textContent).toBe("false");
  });

  it("handles mutation success for JSON and CSV and handles error", async () => {
    let mutationOptions: any;
    mockUseMutation.mockImplementation((options: any) => {
      mutationOptions = options;
      return { mutate: mockMutate, isPending: false };
    });
    formMock.getFieldValue.mockImplementation((field: string) => {
      if (field === "format") return EExportFormat.JSON;
      return undefined;
    });

    render(<ExportBtn model="Event" filters={{}} />);

    await mutationOptions.mutationFn({ limit: 5 });
    expect(mockPostFetcher).toHaveBeenCalledWith(
      expect.stringContaining("/export/Event?"),
      { limit: 5 },
    );

    mutationOptions.onSuccess({ rows: [1] });
    expect(mockFileDownload).toHaveBeenCalledWith('{"rows":[1]}', "Event.json");
    expect(formMock.resetFields).toHaveBeenCalled();
    expect(mockMessageSuccess).toHaveBeenCalledWith("Successfully exported");

    formMock.getFieldValue.mockImplementation((field: string) => {
      if (field === "format") return EExportFormat.CSV;
      return undefined;
    });
    mutationOptions.onSuccess("a,b,csv");
    expect(mockFileDownload).toHaveBeenCalledWith("a,b,csv", "Event.csv");

    mutationOptions.onError();
    expect(mockMessageError).toHaveBeenCalledWith("Server error");
  });
});
