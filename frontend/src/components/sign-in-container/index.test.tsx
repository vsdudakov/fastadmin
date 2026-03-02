import { QueryClient } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";
import { SignInContainer } from "@/components/sign-in-container";
import { ROUTES } from "@/constants/routes";
import { TestProviders } from "@/providers";
import { SignInUserContext } from "@/providers/SignInUserProvider";

const { navigateMock } = vi.hoisted(() => ({
  navigateMock: vi.fn(),
}));

vi.mock("react-router-dom", async () => {
  const actual =
    await vi.importActual<typeof import("react-router-dom")>(
      "react-router-dom",
    );
  return {
    ...actual,
    useNavigate: () => navigateMock,
  };
});

test("Renders SignInContainer", () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <SignInUserContext.Provider
        value={{
          signedIn: false,
          signedInUser: undefined,
          signedInUserRefetch: () => Promise.resolve(undefined as any),
        }}
      >
        <SignInContainer title="Sign In">
          <div data-testid="form">Form content</div>
        </SignInContainer>
      </SignInUserContext.Provider>
    </TestProviders>,
  );
  expect(screen.getByTestId("form")).toBeTruthy();
  expect(screen.getByText("Form content")).toBeTruthy();
});

test("redirects to home when already signed in", () => {
  const queryClient = new QueryClient();

  render(
    <TestProviders client={queryClient}>
      <SignInUserContext.Provider
        value={{
          signedIn: true,
          signedInUser: undefined,
          signedInUserRefetch: () => Promise.resolve(undefined as any),
        }}
      >
        <SignInContainer title="Sign In">
          <div data-testid="form">Form content</div>
        </SignInContainer>
      </SignInUserContext.Provider>
    </TestProviders>,
  );

  expect(navigateMock).toHaveBeenCalledWith(ROUTES.HOME);
});
