import { QueryClient } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { test } from "vitest";

import { Cards } from "@/components/table-or-cards/cards";
import { TestProviders } from "@/providers";

test("Renders Cards", () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <Cards />
    </TestProviders>,
  );
});
