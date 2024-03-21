import { QueryClient } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { test } from "vitest";

import { ExportBtn } from "@/components/export-btn";
import { TestProviders } from "@/providers";

test("Renders ExportBtn", () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <ExportBtn />
    </TestProviders>,
  );
});
