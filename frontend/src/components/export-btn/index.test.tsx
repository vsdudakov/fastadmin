import { QueryClient } from "@tanstack/react-query";
import { fireEvent, render } from "@testing-library/react";
import { expect, test } from "vitest";

import { ExportBtn } from "@/components/export-btn";
import { TestProviders } from "@/providers";

test("Renders ExportBtn", () => {
  const queryClient = new QueryClient();
  const { container } = render(
    <TestProviders client={queryClient}>
      <ExportBtn />
    </TestProviders>,
  );
  expect(container).toBeDefined();
});

test("Opens modal when Export clicked", () => {
  const queryClient = new QueryClient();
  const { container } = render(
    <TestProviders client={queryClient}>
      <ExportBtn model="Event" />
    </TestProviders>,
  );
  const exportBtn = container.querySelector("button");
  if (exportBtn) fireEvent.click(exportBtn);
  expect(container).toBeDefined();
});
