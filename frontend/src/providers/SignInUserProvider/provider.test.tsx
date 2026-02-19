import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { SignInUserContext } from "@/providers/SignInUserProvider";

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

import { SignInUserProvider } from "./provider";

const ContextReader = () => (
  <SignInUserContext.Consumer>
    {({ signedIn, signedInUser }) => (
      <div data-testid="context">
        {signedIn ? "signed-in" : "signed-out"}:
        {signedInUser?.username || "none"}
      </div>
    )}
  </SignInUserContext.Consumer>
);

describe("SignInUserProvider", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("returns null while loading", () => {
    mockUseQuery.mockReturnValue({
      isLoading: true,
      isError: false,
    });

    render(
      <SignInUserProvider>
        <div data-testid="child">child</div>
      </SignInUserProvider>,
    );

    expect(screen.queryByTestId("child")).toBeNull();
  });

  it("provides signed-in context when query succeeds", async () => {
    const refetch = vi.fn();
    mockUseQuery.mockReturnValue({
      isLoading: false,
      isError: false,
      data: { username: "admin" },
      refetch,
    });

    render(
      <SignInUserProvider>
        <ContextReader />
      </SignInUserProvider>,
    );

    expect(screen.getByTestId("context").textContent).toContain(
      "signed-in:admin",
    );
    expect(mockUseQuery).toHaveBeenCalledWith(
      expect.objectContaining({
        queryKey: ["/me"],
        retry: false,
        refetchOnWindowFocus: false,
        queryFn: expect.any(Function),
      }),
    );

    const useQueryOptions = mockUseQuery.mock.calls[0][0] as {
      queryFn: () => Promise<unknown>;
    };
    await useQueryOptions.queryFn();
    expect(mockGetFetcher).toHaveBeenCalledWith("/me");
  });

  it("provides signed-out context when query errors", () => {
    mockUseQuery.mockReturnValue({
      isLoading: false,
      isError: true,
      data: undefined,
      refetch: vi.fn(),
    });

    render(
      <SignInUserProvider>
        <ContextReader />
      </SignInUserProvider>,
    );

    expect(screen.getByTestId("context").textContent).toContain(
      "signed-out:none",
    );
  });
});
