import { QueryClient } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { expect, test } from "vitest";

import { PasswordInput } from "@/components/password-input";
import { TestProviders } from "@/providers";

test("Renders PasswordInput with parentId", () => {
  const queryClient = new QueryClient();
  const { container } = render(
    <TestProviders client={queryClient}>
      <PasswordInput parentId="user-1" />
    </TestProviders>,
  );
  expect(container).toBeDefined();
});

test("Renders PasswordInput without parentId", () => {
  const queryClient = new QueryClient();
  const { container } = render(
    <TestProviders client={queryClient}>
      <PasswordInput />
    </TestProviders>,
  );
  expect(container).toBeDefined();
});
