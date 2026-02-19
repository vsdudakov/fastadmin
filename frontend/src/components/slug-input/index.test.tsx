import { QueryClient } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { expect, test } from "vitest";

import { SlugInput } from "@/components/slug-input";
import { TestProviders } from "@/providers";

test("Renders SlugInput", () => {
  const queryClient = new QueryClient();
  const { container } = render(
    <TestProviders client={queryClient}>
      <SlugInput />
    </TestProviders>,
  );
  expect(container).toBeDefined();
});
