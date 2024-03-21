import { QueryClient } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { test } from "vitest";

import { SignIn } from "@/containers/sign-in";
import { TestProviders } from "@/providers";

test("Renders SignIn", () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <SignIn />
    </TestProviders>,
  );
});
