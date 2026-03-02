import { QueryClient } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/providers/SignInUserProvider/provider", () => ({
  SignInUserProvider: ({ children }: { children?: React.ReactNode }) => (
    <>{children}</>
  ),
}));

vi.mock("@/providers/ConfigurationProvider/provider", () => ({
  ConfigurationProvider: ({ children }: { children?: React.ReactNode }) => (
    <>{children}</>
  ),
}));

import {
  ExternalProviders,
  InternalProviders,
  TestProviders,
} from "./providers";

describe("Providers", () => {
  it("renders children within InternalProviders", () => {
    const client = new QueryClient();

    render(
      <ExternalProviders client={client}>
        <InternalProviders>
          <div data-testid="internal-child">internal</div>
        </InternalProviders>
      </ExternalProviders>,
    );

    expect(screen.getByTestId("internal-child")).toBeTruthy();
  });

  it("renders children within ExternalProviders", () => {
    const client = new QueryClient();

    render(
      <ExternalProviders client={client}>
        <div data-testid="external-child">external</div>
      </ExternalProviders>,
    );

    expect(screen.getByTestId("external-child")).toBeTruthy();
  });

  it("renders children within TestProviders", () => {
    const client = new QueryClient();

    render(
      <TestProviders client={client}>
        <div data-testid="test-child">test</div>
      </TestProviders>,
    );

    expect(screen.getByTestId("test-child")).toBeTruthy();
  });
});
