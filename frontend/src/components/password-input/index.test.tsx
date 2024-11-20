import { QueryClient } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { test } from "vitest";

import { PasswordInput } from "@/components/password-input";
import { TestProviders } from "@/providers";

test("Renders PasswordInput", () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <PasswordInput parentId="test" />
    </TestProviders>,
  );
});
