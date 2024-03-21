import { QueryClient } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { test } from "vitest";

import { SlugInput } from "@/components/slug-input";
import { TestProviders } from "@/providers";

test("Renders SlugInput", () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <SlugInput />
    </TestProviders>,
  );
});
