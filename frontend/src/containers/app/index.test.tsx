import { QueryClient } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { expect, test } from "vitest";

import { App } from "@/containers/app";
import { TestProviders } from "@/providers";

test("Renders App", () => {
  const queryClient = new QueryClient();
  const { container } = render(
    <TestProviders client={queryClient}>
      <App />
    </TestProviders>,
  );
  expect(container).toBeDefined();
});
