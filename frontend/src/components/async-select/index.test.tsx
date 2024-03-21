import { QueryClient } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { test } from "vitest";

import { AsyncSelect } from "@/components/async-select";
import { TestProviders } from "@/providers";

test("Renders AsyncTransfer", () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <AsyncSelect idField="id" labelFields={["id"]} parentModel="test" />
    </TestProviders>,
  );
});
