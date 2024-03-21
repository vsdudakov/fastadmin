import { QueryClient } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { test } from "vitest";

import { JsonTextArea } from "@/components/json-textarea";
import { TestProviders } from "@/providers";

test("Renders JsonTextArea", () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <JsonTextArea />
    </TestProviders>,
  );
});
