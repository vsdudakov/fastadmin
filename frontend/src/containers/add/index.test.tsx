import { QueryClient } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { test } from "vitest";

import { Add } from "@/containers/add";
import { TestProviders } from "@/providers";

test("Renders Add", () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <Add />
    </TestProviders>,
  );
});
