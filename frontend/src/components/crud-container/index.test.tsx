import { QueryClient } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { test } from "vitest";

import { CrudContainer } from "@/components/crud-container";
import { TestProviders } from "@/providers";

test("Renders CrudContainer", () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <CrudContainer title="test">
        <div />
      </CrudContainer>
    </TestProviders>,
  );
});
