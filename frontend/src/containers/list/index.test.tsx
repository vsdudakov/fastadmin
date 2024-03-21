import { QueryClient } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { test } from "vitest";

import { List } from "@/containers/list";
import { TestProviders } from "@/providers";

test("Renders List", () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <List />
    </TestProviders>,
  );
});
