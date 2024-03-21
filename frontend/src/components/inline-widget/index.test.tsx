import { QueryClient } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { test } from "vitest";

import { InlineWidget } from "@/components/inline-widget";
import { TestProviders } from "@/providers";

test("Renders AsyncTransfer", () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <InlineWidget
        parentId="test"
        modelConfiguration={{
          name: "Test",
          fields: [],
          permissions: [],
          actions: [],
          fk_name: "parent",
        }}
      />
    </TestProviders>,
  );
});
