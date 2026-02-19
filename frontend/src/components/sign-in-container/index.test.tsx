import { QueryClient } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import { SignInContainer } from "@/components/sign-in-container";
import { TestProviders } from "@/providers";
import { SignInUserContext } from "@/providers/SignInUserProvider";

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
