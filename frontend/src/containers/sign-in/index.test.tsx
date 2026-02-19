import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import type React from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ConfigurationContext } from "@/providers/ConfigurationProvider";
import { SignInUserContext } from "@/providers/SignInUserProvider";
import { SignIn } from "./index";

const {
  mockUseMutation,
  mockMutateSignIn,
  mockPostFetcher,
  mockHandleError,
  mockSignedInUserRefetch,
  formMock,
} = vi.hoisted(() => ({
  mockUseMutation: vi.fn(),
  mockMutateSignIn: vi.fn(),
  mockPostFetcher: vi.fn(),
  mockHandleError: vi.fn(),
  mockSignedInUserRefetch: vi.fn(),
  formMock: {},
}));

vi.mock("@tanstack/react-query", () => ({
  useMutation: (options: unknown) => mockUseMutation(options),
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
  theme: {
    useToken: () => ({ token: { colorPrimary: "#000" } }),
  },
  Form: Object.assign(
    ({
      children,
      onFinish,
    }: {
      children: React.ReactNode;
      onFinish?: (data: unknown) => void;
    }) => (
      <div>
        <button
          type="button"
          onClick={() => onFinish?.({ username: "u", password: "p" })}
        >
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
  Card: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Row: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Col: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Space: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Image: ({ alt }: { alt: string }) => <img alt={alt} />,
  Input: Object.assign(
    ({ placeholder }: { placeholder?: string }) => (
      <input placeholder={placeholder} />
    ),
    {
      Password: ({ placeholder }: { placeholder?: string }) => (
        <input placeholder={placeholder} type="password" />
      ),
    },
  ),
  Button: ({ children }: { children: React.ReactNode }) => (
    <button type="button">{children}</button>
  ),
}));

vi.mock("@/components/sign-in-container", () => ({
  SignInContainer: ({
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

vi.mock("@/fetchers/fetchers", () => ({
  postFetcher: (...args: unknown[]) => mockPostFetcher(...args),
}));

vi.mock("@/helpers/forms", () => ({
  handleError: (...args: unknown[]) => mockHandleError(...args),
}));

vi.mock("@/helpers/title", () => ({
  getTitleFromFieldName: (v: string) => v,
}));

describe("SignIn container", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseMutation.mockReturnValue({
      mutate: mockMutateSignIn,
      isPending: false,
    });
  });

  afterEach(() => {
    cleanup();
  });

  it("submits sign-in data via mutate", () => {
    render(
      <ConfigurationContext.Provider
        value={
          {
            configuration: { site_name: "Admin", username_field: "username" },
          } as any
        }
      >
        <SignInUserContext.Provider
          value={{ signedInUserRefetch: mockSignedInUserRefetch } as any}
        >
          <SignIn />
        </SignInUserContext.Provider>
      </ConfigurationContext.Provider>,
    );

    fireEvent.click(screen.getByRole("button", { name: "trigger-submit" }));
    expect(mockMutateSignIn).toHaveBeenCalledWith({
      username: "u",
      password: "p",
    });
  });

  it("covers mutation function and success/error callbacks", async () => {
    render(
      <ConfigurationContext.Provider
        value={
          {
            configuration: { site_name: "Admin", username_field: "username" },
          } as any
        }
      >
        <SignInUserContext.Provider
          value={{ signedInUserRefetch: mockSignedInUserRefetch } as any}
        >
          <SignIn />
        </SignInUserContext.Provider>
      </ConfigurationContext.Provider>,
    );

    const mutationOptions = mockUseMutation.mock.calls[0][0] as {
      mutationFn: (payload: unknown) => Promise<unknown> | unknown;
      onSuccess: () => void;
      onError: (error: Error) => void;
    };

    await mutationOptions.mutationFn({ username: "john" });
    expect(mockPostFetcher).toHaveBeenCalledWith("/sign-in", {
      username: "john",
    });

    mutationOptions.onSuccess();
    expect(mockSignedInUserRefetch).toHaveBeenCalled();

    mutationOptions.onError(new Error("invalid credentials"));
    expect(mockHandleError).toHaveBeenCalledWith(expect.any(Error), formMock);
  });
});
