import { QueryClient } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { test } from "vitest";

import { Change } from "@/containers/change";
import { TestProviders } from "@/providers";

test("Renders Change", () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <Change />
    </TestProviders>,
  );
});
